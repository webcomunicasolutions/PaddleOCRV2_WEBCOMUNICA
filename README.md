# 🚀 PaddleOCR 2.8.1 - Optimizado para CPU - Versión WebComunica

**Servidor PaddleOCR con la mejor configuración para detectar bloques en horizontal y vertical**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.8.1-green)](https://github.com/PaddlePaddle/PaddleOCR)
[![Flask](https://img.shields.io/badge/Flask-Production-red)](https://flask.palletsprojects.com/)
[![CPU](https://img.shields.io/badge/CPU-Optimized-orange)](.)

## 🎯 Descripción

Servidor PaddleOCR con la mejor configuración para detectar bloques en horizontal y vertical. Lo he optimizado para un proyecto que tengo de lectura de facturas, tickets, albaranes, etc. Utilizando PaddleOCR 2.8.1 con configuración probada que supera ampliamente las versiones estándar.

### 🏆 Resultados Probados

| Métrica | Configuración Optimizada | Estándar |
|---------|------------------------|----------|
| **Bloques detectados** | **79+** | 64 |
| **Confianza promedio** | **97.5%** | ~85% |
| **Tiempo procesamiento** | **0.87s** | 2-3s |
| **Orientaciones** | **Horizontal + Vertical** | Solo horizontal |
| **Soporte PDF** | **Nativo** | Conversión manual |
| **Requerimientos** | **Solo CPU** | GPU recomendada |

## ✨ Características Principales

- **🏆 Configuración Optimizada Probada**: 79+ bloques detectados vs 64 estándar
- **⚡ Ultra Rápido**: <1 segundo de procesamiento por documento
- **💻 CPU Optimizado**: Sin dependencias CUDA, funciona en cualquier servidor
- **📄 Soporte Completo**: PDF nativo, imágenes, documentos escaneados
- **🌍 Multi-idioma**: Español e Inglés optimizados
- **🔍 Análisis Visual**: Endpoint `/analyze` con formato ultra detallado
- **🔒 Nivel Empresarial**: Rate limiting, logging, auditoría, seguridad
- **🐳 Deploy Inmediato**: Docker + Docker Compose listo para producción

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (⭐ Recomendada)

```bash
# 1. Clonar repositorio
git clone https://github.com/webcomunicasolutions/PaddleOCRV2_WEBCOMUNICA.git
cd PaddleOCRV2_WEBCOMUNICA

# 2. Ejecutar instalación automática
chmod +x setup.sh
./setup.sh install

# 3. ¡Listo! Servidor disponible en http://localhost:8501
```

### Opción 2: Manual

```bash
# Construir y ejecutar
docker build -t ocr-server-cpu .
docker-compose up -d

# Verificar
curl http://localhost:8501/health
```

## 📡 API - Guía de Uso

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Dashboard empresarial con métricas en tiempo real |
| `/health` | GET | Estado del servidor y configuración |
| `/stats` | GET | Estadísticas detalladas de rendimiento |
| `/process` | POST | Procesamiento OCR estándar |
| `/analyze` | POST | **⭐ Análisis visual ultra completo** |

### Ejemplos Prácticos

#### 1. Análisis Visual Ultra Completo (⭐ RECOMENDADO)

```bash
# Ver TODOS los bloques con formato visual espectacular
curl -X POST http://localhost:8501/analyze \
  -F "file=@factura.pdf" \
  -F "language=es" | jq -r '.ultra_analysis'
```

**Salida esperada:**
```
🏆 CONFIGURACIÓN OPTIMIZADA - TODOS LOS BLOQUES:
📊 Total bloques: 79
🎯 Confianza: 97.5%
⚡ Tiempo: 0.873s
============================================================
 1. ↔️ "FACTURA RECTIFICATIVA" (0.998)
 2. ↔️ "ROH COMPANY" (0.995)
 3. ↕️ "Datos Fiscales" (1.000)
 4. ↔️ "B12345678" (0.987)
...
79. ↔️ "dpto.juridico@empresa.es" (0.998)
============================================================
📊 Orientaciones: 70 horiz, 9 vert, 0 rotadas
```

#### 2. Procesamiento para Automatización

```bash
# Extraer solo el texto para scripts
curl -X POST http://localhost:8501/process \
  -F "file=@documento.pdf" \
  -F "language=es" | jq -r '.text'
```

#### 3. Procesamiento Detallado con Coordenadas

```bash
# Para extracción de datos específicos
curl -X POST http://localhost:8501/process \
  -F "file=@factura.pdf" \
  -F "language=es" \
  -F "detailed=true"
```

**Respuesta típica:**
```json
{
  "success": true,
  "text": "FACTURA\\nEMPRESA EJEMPLO\\n...",
  "total_blocks": 79,
  "avg_confidence": 0.975,
  "processing_time": 0.873,
  "ocr_version": "2.8.1-CPU-OPTIMIZADO",
  "blocks": [
    {
      "text": "FACTURA",
      "confidence": 0.998,
      "coordinates": [[100,50], [200,50], [200,80], [100,80]],
      "orientation": "horizontal"
    }
  ]
}
```

## 🛠️ Casos de Uso Empresariales

### 1. Digitalización Masiva de Facturas

```python
import requests
import json

def procesar_facturas(directorio_facturas):
    """Procesar múltiples facturas automáticamente"""
    resultados = []
    
    for archivo in glob.glob(f"{directorio_facturas}/*.pdf"):
        with open(archivo, 'rb') as f:
            response = requests.post(
                'http://localhost:8501/process',
                files={'file': f},
                data={'language': 'es', 'detailed': 'true'}
            )
            
            if response.status_code == 200:
                data = response.json()
                resultados.append({
                    'archivo': archivo,
                    'bloques': data['total_blocks'],
                    'confianza': data['avg_confidence'],
                    'texto': data['text']
                })
                print(f"✅ {archivo}: {data['total_blocks']} bloques")
            
    return resultados
```

### 2. Integración con ERP/CRM

```python
class OCRIntegrator:
    def __init__(self, ocr_url="http://localhost:8501"):
        self.ocr_url = ocr_url
    
    def extraer_datos_factura(self, archivo_pdf):
        """Extraer datos específicos de facturas"""
        response = requests.post(
            f"{self.ocr_url}/process",
            files={'file': open(archivo_pdf, 'rb')},
            data={'language': 'es', 'detailed': 'true'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extracción inteligente de campos
            texto = data['text']
            return {
                'numero_factura': self._extraer_numero(texto),
                'fecha': self._extraer_fecha(texto),
                'total': self._extraer_total(texto),
                'proveedor': self._extraer_proveedor(texto),
                'confianza_global': data['avg_confidence']
            }
```

### 3. Script de Procesamiento Masivo

```bash
#!/bin/bash
# Procesar todos los PDFs de un directorio

INPUT_DIR="./data/input"
OUTPUT_DIR="./data/output"

echo "🔄 Iniciando procesamiento masivo..."

for file in "$INPUT_DIR"/*.pdf; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .pdf)
        echo "📄 Procesando: $filename"
        
        # Análisis completo con resultados guardados
        curl -s -X POST http://localhost:8501/analyze \
          -F "file=@$file" \
          -F "language=es" \
          > "$OUTPUT_DIR/${filename}_analysis.json"
        
        echo "✅ Completado: $filename"
    fi
done

echo "🎉 Procesamiento masivo finalizado"
```

## ⚙️ Configuración y Deployment

### Docker Compose para Producción

```yaml
version: '3.8'
services:
  paddleocr-cpu:
    build: .
    container_name: ocr-server-cpu
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - paddleocr-cpu-models:/app/.paddleocr
    environment:
      - PYTHONUNBUFFERED=1
      - OMP_NUM_THREADS=4
      - MKL_NUM_THREADS=4
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '4.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
      interval: 30s
      timeout: 15s
      retries: 3

volumes:
  paddleocr-cpu-models:
```

### Variables de Entorno

```bash
# Recursos del sistema
MAX_FILE_SIZE_MB=50
RATE_LIMIT_REQUESTS=100
CPU_THREADS=4

# OCR
DEFAULT_LANGUAGE=es
SUPPORTED_LANGUAGES=es,en

# Empresa
COMPANY_NAME="Tu Empresa"
ENVIRONMENT=production
```

## 🔧 Gestión y Monitoreo

### Comandos de Gestión

```bash
# Ver estado completo
./setup.sh status

# Logs en tiempo real
./setup.sh logs

# Reiniciar servicio
./setup.sh restart

# Actualizar servidor
./setup.sh update

# Limpiar sistema
./setup.sh clean
```

### Monitoreo de Rendimiento

```bash
# Estadísticas del servidor
curl http://localhost:8501/stats | jq '.server_stats'

# Ver recursos en tiempo real
docker stats ocr-server-cpu

# Health check automatizado
curl -f http://localhost:8501/health || echo "❌ Servidor no responde"
```

## 🧪 Testing y Validación

### Tests Básicos

```bash
# Test de funcionamiento
curl -f http://localhost:8501/health || echo "❌ Health check falló"

# Test con documento real
curl -X POST http://localhost:8501/process \
  -F "file=@test.pdf" \
  -F "language=es" | jq '.total_blocks'

# Test de análisis visual
curl -X POST http://localhost:8501/analyze \
  -F "file=@test.pdf" \
  -F "language=es" | jq -r '.ultra_analysis'
```

### Validación de Calidad

```bash
#!/bin/bash
echo "🧪 Validando calidad OCR..."

for file in test-documents/*.pdf; do
    result=$(curl -s -X POST http://localhost:8501/process \
             -F "file=@$file" -F "language=es")
    
    blocks=$(echo "$result" | jq '.total_blocks')
    confidence=$(echo "$result" | jq '.avg_confidence')
    
    echo "📊 $(basename "$file"): $blocks bloques, ${confidence}% confianza"
    
    # Validar métricas mínimas para empresa
    if (( $(echo "$confidence > 0.85" | bc -l) )); then
        echo "  ✅ Calidad empresarial"
    else
        echo "  ⚠️ Revisar calidad"
    fi
done
```

## 🔍 Troubleshooting

### Problemas Comunes

#### Servidor no responde
```bash
# Verificar contenedor
docker ps | grep ocr-server-cpu

# Ver logs detallados
docker-compose logs ocr-server-cpu -f

# Reiniciar servicio
docker-compose restart ocr-server-cpu
```

#### Memoria insuficiente
```bash
# Verificar uso de memoria
docker stats --no-stream

# Aumentar límites
# Editar docker-compose.yml -> memory: 6G
```

#### Modelos no se descargan
```bash
# Verificar conectividad
docker-compose exec paddleocr-cpu ping paddleocr.bj.bcebos.com

# Forzar descarga
docker-compose exec paddleocr-cpu python3 -c "
import paddleocr
ocr = paddleocr.PaddleOCR(lang='es')
print('✅ Modelos descargados')
"
```

## 📊 Especificaciones Técnicas

### Configuración Optimizada

```python
# Parámetros optimizados que logran 79+ bloques
paddleocr.PaddleOCR(
    use_angle_cls=True,           # ✅ CRÍTICO: Detección de ángulos
    lang='es',                    # ✅ Idioma optimizado
    use_gpu=False,                # ✅ CPU optimizado
    det_db_thresh=0.1,            # 🏆 MUY sensible (más detección)
    det_db_box_thresh=0.4,        # 🏆 MUY sensible (más cajas)
    drop_score=0.2,               # 🏆 MUY permisivo (más texto)
    enable_mkldnn=True,           # ✅ Aceleración Intel CPU
    cpu_threads=4                 # ✅ Paralelización optimizada
)
```

### Requisitos del Sistema

| Configuración | CPU | RAM | Throughput | Uso |
|---------------|-----|-----|------------|-----|
| **Mínima** | 2 cores | 3GB | ~10 docs/min | Desarrollo |
| **Recomendada** | 4 cores | 4GB | ~20 docs/min | **Producción** |
| **Alto Rendimiento** | 6+ cores | 6GB+ | ~40 docs/min | Carga alta |

### Formatos Soportados

- **PDF**: Nativo (recomendado)
- **Imágenes**: JPG, PNG, BMP, TIFF
- **Tamaño máximo**: 50MB por archivo
- **Resolución**: Automática (optimizada)
- **Orientaciones**: Horizontal, vertical, rotado

## 🔒 Seguridad Empresarial

### Funciones de Seguridad

- **🛡️ Rate Limiting**: 100 req/min por IP
- **📁 Validación**: Tipos y tamaños de archivo
- **🔐 Contenedor Seguro**: Usuario no-root
- **📝 Auditoría**: Logging completo
- **⚠️ Manejo de Errores**: Sin exposición de datos

### Configuración de Seguridad

```nginx
# Configuración Nginx para proxy seguro
upstream ocr_backend {
    server localhost:8501;
}

server {
    listen 80;
    client_max_body_size 50M;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        limit_req zone=ocr_limit burst=20;
        proxy_pass http://ocr_backend;
    }
}
```

## 📁 Estructura del Proyecto

```
PaddleOCRV2_WEBCOMUNICA/
├── 📄 app.py                    # Servidor principal (configuración GANADORA)
├── 🐳 Dockerfile               # Imagen optimizada CPU + PyMuPDF + jq
├── 🔧 docker-compose.yml       # Orquestación completa
├── 🚀 setup.sh                 # Script instalación automática
├── 📚 README.md                # Esta documentación
├── 📊 data/
│   ├── input/                  # Archivos para procesar
│   ├── output/                 # Resultados OCR
│   └── logs/                   # Logs del sistema
├── ⚙️ config/                  # Configuraciones
└── 🗄️ volumes/
    └── paddleocr-models/       # Modelos persistentes
```

## 🎉 Empezar Ahora

```bash
# Instalación completa en 3 comandos
git clone https://github.com/webcomunicasolutions/PaddleOCRV2_WEBCOMUNICA.git
cd PaddleOCRV2_WEBCOMUNICA
./setup.sh install

# Probar análisis visual ultra completo
curl -X POST http://localhost:8501/analyze \
  -F "file=@tu-documento.pdf" \
  -F "language=es" | jq -r '.ultra_analysis'

# ¡Disfruta de 79+ bloques detectados con 97.5% de confianza! 🎉
```

## 📞 Soporte

- **Website**: [https://webcomunica.solutions/](https://webcomunica.solutions/)
- **Instagram**: [WebComunica Soluciones](https://www.instagram.com/stories/webcomunica_soluciones/)
- **Email**: info@webcomunica.solutions
- **Email Alternativo**: info@optimizaconia.es
- **GitHub Issues**: [Reportar problemas](https://github.com/webcomunicasolutions/PaddleOCRV2_WEBCOMUNICA/issues)

---

**🏆 Servidor OCR con Configuración Optimizada - 79+ bloques, 97.5% confianza, <1s**

*Desarrollado con ❤️ por WebComunica Soluciones Informáticas - Mantenimiento informático para PYMES*
