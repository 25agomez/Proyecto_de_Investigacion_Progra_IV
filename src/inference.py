"""
Script de inferencia para modelos locales vía Ollama.
Ejecuta un prompt o una suite completa, mide TTFT y tokens/s
y guarda los resultados en CSV y JSON.
"""
import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime

import requests

# El host se lee de una variable de entorno: sin rutas ni credenciales fijas
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def parse_args():
    p = argparse.ArgumentParser(description="Inferencia local con Ollama")
    p.add_argument("--model", required=True, help="Etiqueta del modelo en Ollama")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt", help="Un prompt directo")
    g.add_argument("--prompts-file", help="Archivo JSON con la suite")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--runs", type=int, default=1, help="Repeticiones de la suite")
    p.add_argument("--output-dir", default="results")
    return p.parse_args()


def generate(model, prompt, temperature, max_tokens):
    """Envía un prompt con streaming y devuelve texto + métricas."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    start = time.perf_counter()
    ttft = None
    parts = []
    final = {}

    try:
        with requests.post(url, json=payload, stream=True, timeout=600) as r:
            if r.status_code == 404:
                raise RuntimeError(
                    f"Modelo '{model}' no encontrado. Ejecuta: ollama pull {model}"
                )
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                text = chunk.get("response", "")
                if text and ttft is None:
                    ttft = time.perf_counter() - start  # primer token
                parts.append(text)
                if chunk.get("done"):
                    final = chunk
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"No se pudo conectar a {OLLAMA_HOST}. ¿Está corriendo Ollama?"
        )

    total = time.perf_counter() - start
    tokens = final.get("eval_count", 0)
    eval_ns = final.get("eval_duration", 0)
    tps = tokens / (eval_ns / 1e9) if eval_ns else 0.0

    return {
        "salida": "".join(parts),
        "tokens_generados": tokens,
        "ttft_s": round(ttft, 3) if ttft else None,
        "tokens_por_s": round(tps, 2),
        "tiempo_total_s": round(total, 3),
    }


def load_prompts(args):
    if args.prompt:
        return [{"id": "manual", "categoria": "manual", "prompt": args.prompt}]
    with open(args.prompts_file, encoding="utf-8") as f:
        return json.load(f)


def main():
    args = parse_args()
    prompts = load_prompts(args)
    os.makedirs(args.output_dir, exist_ok=True)
    rows = []

    for run in range(1, args.runs + 1):
        for item in prompts:
            print(f"[run {run}] {item['id']} ...", flush=True)
            try:
                m = generate(args.model, item["prompt"], args.temperature, args.max_tokens)
            except RuntimeError as e:
                print(f"ERROR: {e}", file=sys.stderr)
                sys.exit(1)
            rows.append({
                "run": run,
                "id": item["id"],
                "categoria": item["categoria"],
                "modelo": args.model,
                "temperatura": args.temperature,
                "prompt": item["prompt"],
                **m,
            })

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.join(args.output_dir, f"{args.model.replace(':', '_').replace('/', '_')}_{stamp}")
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    with open(base + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Resultados guardados en {base}.json y .csv")


if __name__ == "__main__":
    main()