# Dockerfile CPU Optimizado - Con jq y PyMuPDF
FROM python:3.10-slim

# Metadatos
LABEL maintainer="Tu Empresa de Mantenimiento Informático"
LABEL version="3.0-cpu-optimized"
LABEL description="Servidor OCR CPU optimizado sin dependencias CUDA"

# Variables de entorno optimizadas para CPU
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

# Instalar dependencias del sistema optimizadas para CPU + JQ
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar PaddlePaddle CPU y dependencias optimizadas + PyMuPDF
RUN pip install --no-cache-dir \
    paddlepaddle==2.6.1 \
    paddleocr==2.8.1 \
    flask==2.3.3 \
    waitress==2.1.2 \
    opencv-python-headless==4.8.0.76 \
    pillow==10.0.0 \
    numpy==1.24.3 \
    pdf2image==1.16.3 \
    PyMuPDF==1.23.3 \
    requests

# Directorio de trabajo
WORKDIR /app

# Crear estructura de directorios con permisos
RUN mkdir -p /app/data/input \
             /app/data/output \
             /app/data/logs \
             /app/.paddleocr \
    && chmod -R 777 /app

# Variables de entorno para PaddleOCR CPU
ENV PADDLE_HOME=/app/.paddleocr
ENV FLAGS_allocator_strategy=auto_growth
ENV FLAGS_fraction_of_gpu_memory_to_use=0
ENV CUDA_VISIBLE_DEVICES=""

# Copiar aplicación
COPY app.py /app/app.py

# Permisos de ejecución
RUN chmod +x /app/app.py

# Volúmenes
VOLUME ["/app/.paddleocr", "/app/data"]

# Puerto
EXPOSE 8501

# Health check optimizado
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Comando de inicio
CMD ["python", "/app/app.py"]
