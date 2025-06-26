# Dockerfile Empresarial - PaddleOCR Server v3.0
# Optimizado para producción con servidor WSGI

FROM paddlepaddle/paddle:2.6.1-gpu-cuda12.0-cudnn8.9-trt8.6

# Metadatos empresariales
LABEL maintainer="Tu Empresa de Mantenimiento Informático"
LABEL version="3.0-enterprise"
LABEL description="Servidor OCR empresarial con PaddleOCR 2.8.1 optimizado"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Instalar dependencias del sistema para producción
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

# Instalar PaddleOCR estable con configuración probada
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
    pillow==10.0.0

# Crear usuario no-root para seguridad
RUN groupadd -r ocruser && useradd -r -g ocruser ocruser

# Directorio de trabajo
WORKDIR /app

# Crear estructura de directorios empresarial
RUN mkdir -p /app/data/input \
             /app/data/output \
             /app/data/logs \
             /app/config \
             /app/scripts \
    && chown -R ocruser:ocruser /app

# Copiar aplicación
COPY app.py /app/app.py
COPY healthcheck.py /app/healthcheck.py

# Script de healthcheck personalizado
RUN echo '#!/usr/bin/env python3\n\
import requests\n\
import sys\n\
try:\n\
    response = requests.get("http://localhost:8501/health", timeout=10)\n\
    if response.status_code == 200 and response.json().get("ocr_ready"):\n\
        sys.exit(0)\n\
    else:\n\
        sys.exit(1)\n\
except:\n\
    sys.exit(1)\n' > /app/healthcheck.py && chmod +x /app/healthcheck.py

# Configurar permisos
RUN chown -R ocruser:ocruser /app \
    && chmod +x /app/app.py

# Volúmenes empresariales
VOLUME ["/root/.paddleocr", "/app/data", "/app/config"]

# Cambiar a usuario no-root
USER ocruser

# Healthcheck empresarial
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD python /app/healthcheck.py

# Puerto de la aplicación
EXPOSE 8501

# Comando por defecto con servidor de producción
ENTRYPOINT ["python", "/app/app.py"]