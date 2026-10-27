# Imagen base ligera con versión fija (reproducible)
FROM python:3.12.7-slim-bookworm

# Evita .pyc y fuerza salida sin buffer (logs en vivo)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Usuario no root
RUN useradd --create-home --uid 1000 appuser

# 1) Dependencias primero: esta capa se cachea si requirements.txt no cambia
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Código y prompts después (cambian más seguido)
COPY src/ ./src/
COPY prompts/ ./prompts/

# Carpeta de resultados con permisos para el usuario no root
RUN mkdir -p /app/results && chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["python", "src/inference.py"]
CMD ["--help"]