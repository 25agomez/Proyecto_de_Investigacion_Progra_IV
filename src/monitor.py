"""Muestrea RAM y CPU de los procesos de Ollama cada segundo y guarda un CSV."""
import csv
import sys
import time

import psutil

out = sys.argv[1] if len(sys.argv) > 1 else "results/monitor.csv"
peak_ram = 0.0
print("Monitoreando... Ctrl+C para detener")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t_s", "ram_gb", "cpu_pct"])
    t0 = time.time()
    try:
        while True:
            procs = [p for p in psutil.process_iter(["name"])
                     if "ollama" in (p.info["name"] or "").lower()]
            ram = sum(p.memory_info().rss for p in procs) / 1e9
            cpu = sum(p.cpu_percent(interval=None) for p in procs)
            peak_ram = max(peak_ram, ram)
            w.writerow([round(time.time() - t0, 1), round(ram, 2), round(cpu, 1)])
            f.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Memoria pico: {peak_ram:.2f} GB")