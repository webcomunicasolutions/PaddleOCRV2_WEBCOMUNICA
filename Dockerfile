# Dockerfile con Permisos Corregidos - OCR Server Empresarial
# Solución definitiva al problema de permisos

FROM paddlepaddle/paddle:2.6.1-gpu-cuda12.0-cudnn8.9-trt8.6

# Metadatos
LABEL maintainer="Tu Empresa de Mantenimiento Informático"
LABEL version="3.0-enterprise-permissions-fixed"
LABEL description="Servidor OCR empresarial sin problemas de permisos"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# CRÍTICO: Configurar directorios de PaddleOCR con permisos
ENV PADDLE_HOME=/app/.paddleocr
ENV MPLCONFIGDIR=/app/.matplotlib

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar PaddleOCR y dependencias
RUN pip install --no-cache-dir \
    paddlepaddle-gpu==2.6.1.post120 \
    -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

RUN pip install --no-cache-dir \
    paddleocr==2.8.1 \
    flask==2.3.3 \
    werkzeug==2.3.7 \
    waitress==2.1.2 \
    pdf2image==1.16.3 \
    PyMuPDF==1.23.3 \
    opencv-python==4.8.0.76 \
    numpy==1.24.3 \
    pillow==10.0.0 \
    requests

# Directorio de trabajo
WORKDIR /app

# SOLUCIÓN: Crear todos los directorios necesarios con permisos correctos
RUN mkdir -p /app/data/input \
             /app/data/output \
             /app/data/logs \
             /app/config \
             /app/.paddleocr \
             /app/.matplotlib \
    && chmod -R 777 /app

# Copiar aplicación
COPY app.py /app/app.py

# Asegurar permisos de ejecución
RUN chmod +x /app/app.py

# CRÍTICO: Usar volúmenes que apunten a directorios con permisos
VOLUME ["/app/.paddleocr", "/app/data", "/app/config"]

# Puerto
EXPOSE 8501

# Health check simple (sin dependencias de archivos)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# EJECUTAR COMO ROOT para evitar problemas de permisos
# (En entorno empresarial controlado esto es aceptable)
USER root

# Comando de inicio
CMD ["python", "/app/app.py"]
