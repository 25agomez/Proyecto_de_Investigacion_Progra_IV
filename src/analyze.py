"""Calcula promedio y desviación estándar entre corridas y genera gráficos."""
import argparse
import json

# pyrefly: ignore[missing-import]
import matplotlib.pyplot as plt
import pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--config", action="append", required=True, help="etiqueta=ruta.json")
p.add_argument("--out", default="results")
args = p.parse_args()

frames = []
for c in args.config:
    label, path = c.split("=", 1)
    with open(path, encoding="utf-8") as f:
        df = pd.DataFrame(json.load(f))
    df["config"] = label
    frames.append(df)
df = pd.concat(frames)

# 1) promedio por corrida; 2) media y desviación estándar entre las 3 corridas
per_run = df.groupby(["config", "run"])[["ttft_s", "tokens_por_s"]].mean().reset_index()
summary = per_run.groupby("config")[["ttft_s", "tokens_por_s"]].agg(["mean", "std"])
summary.columns = ["_".join(c) for c in summary.columns]
print(summary.round(3))
summary.round(3).to_csv(f"{args.out}/resumen_metricas.csv")

for metric, title, fname in [
    ("ttft_s", "Tiempo al primer token (s)", "grafico_ttft.png"),
    ("tokens_por_s", "Velocidad de generación (tokens/s)", "grafico_tps.png"),
]:
    plt.figure(figsize=(5, 4))
    plt.bar(summary.index, summary[f"{metric}_mean"],
            yerr=summary[f"{metric}_std"], capsize=6)
    plt.ylabel(title)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"{args.out}/{fname}", dpi=150)
print("Gráficos guardados en", args.out)