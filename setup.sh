#!/bin/bash

# Script de Configuración Empresarial - OCR Server v3.0
# Para empresas de mantenimiento informático

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner empresarial
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚀 OCR SERVER EMPRESARIAL v3.0 - CONFIGURACIÓN AUTOMÁTICA ║
║                                                              ║
║    Optimizado para empresas de mantenimiento informático    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Variables de configuración
PROJECT_NAME="ocr-server-enterprise"
DOCKER_IMAGE="ocr-enterprise:latest"
DATA_DIR="./data"
CONFIG_DIR="./config"
LOGS_DIR="./logs"
NGINX_DIR="./nginx"
MONITORING_DIR="./monitoring"

# Verificar requisitos del sistema
check_requirements() {
    log "🔍 Verificando requisitos del sistema..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado. Instálalo desde: https://docs.docker.com/get-docker/"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose no está instalado."
    fi
    
    # Verificar espacio en disco (mínimo 10GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ $AVAILABLE_SPACE -lt 10485760 ]; then  # 10GB en KB
        warn "Espacio en disco bajo. Recomendado: mínimo 10GB libres"
    fi
    
    # Verificar RAM (mínimo 4GB recomendado)
    TOTAL_RAM=$(free -m | awk 'NR==2{print $2}')
    if [ $TOTAL_RAM -lt 4096 ]; then
        warn "RAM baja detectada. Recomendado: mínimo 4GB para rendimiento óptimo"
    fi
    
    log "✅ Requisitos verificados correctamente"
}

# Crear estructura de directorios empresarial
create_directory_structure() {
    log "📁 Creando estructura de directorios empresarial..."
    
    # Directorios principales
    mkdir -p $DATA_DIR/{input,output,logs,backups}
    mkdir -p $CONFIG_DIR
    mkdir -p $LOGS_DIR
    mkdir -p $NGINX_DIR/{ssl,conf.d}
    mkdir -p $MONITORING_DIR
    mkdir -p volumes/paddleocr-models
    
    # Crear archivos de configuración por defecto
    create_config_files
    
    log "✅ Estructura de directorios creada"
}

# Crear archivos de configuración
create_config_files() {
    log "⚙️ Creando archivos de configuración..."
    
    # Configuración Nginx
    cat > $NGINX_DIR/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream ocr_backend {
        server paddleocr-enterprise:8501;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=ocr_limit:10m rate=10r/m;
    
    server {
        listen 80;
        server_name localhost;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # File upload limits
        client_max_body_size 50M;
        
        location / {
            limit_req zone=ocr_limit burst=20 nodelay;
            
            proxy_pass http://ocr_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
        
        # Health check endpoint
        location /health {
            proxy_pass http://ocr_backend/health;
            access_log off;
        }
    }
}
EOF

    # Configuración Prometheus
    cat > $MONITORING_DIR/prometheus.yml << 'EOF'
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'ocr-server'
    static_configs:
      - targets: ['paddleocr-enterprise:8501']
    scrape_interval: 15s
    metrics_path: '/metrics'
EOF

    # Variables de entorno por defecto
    cat > .env << 'EOF'
# Configuración OCR Server Empresarial

# Configuración del servidor
MAX_FILE_SIZE_MB=50
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
DEFAULT_LANGUAGE=es

# Logging
OCR_LOG_LEVEL=INFO
ENABLE_DETAILED_LOGGING=true

# Recursos
CPU_LIMIT=4.0
MEMORY_LIMIT=6G
CPU_RESERVATION=2.0
MEMORY_RESERVATION=3G

# Red
EXTERNAL_PORT=8501
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Empresa
COMPANY_NAME="Tu Empresa de Mantenimiento"
ENVIRONMENT=production
EOF

    log "✅ Archivos de configuración creados"
}

# Construir imagen Docker
build_docker_image() {
    log "🏗️ Construyendo imagen Docker empresarial..."
    
    if [ -f "Dockerfile" ]; then
        docker build -t $DOCKER_IMAGE . --no-cache
        log "✅ Imagen Docker construida: $DOCKER_IMAGE"
    else
        error "Dockerfile no encontrado. Asegúrate de tener el Dockerfile en el directorio actual."
    fi
}

# Configurar permisos de seguridad
setup_security() {
    log "🔒 Configurando permisos de seguridad..."
    
    # Permisos para directorios de datos
    chmod 755 $DATA_DIR
    chmod 755 $DATA_DIR/{input,output,logs,backups}
    
    # Permisos para configuración (solo lectura)
    chmod 644 $CONFIG_DIR/* 2>/dev/null || true
    
    # Crear usuario de sistema si no existe (opcional)
    if ! id "ocruser" &>/dev/null; then
        info "Creando usuario del sistema 'ocruser'..."
        # useradd -r -s /bin/false ocruser 2>/dev/null || warn "No se pudo crear usuario ocruser"
    fi
    
    log "✅ Permisos de seguridad configurados"
}

# Inicializar servicio
start_service() {
    log "🚀 Iniciando OCR Server Empresarial..."
    
    # Parar servicios existentes
    docker-compose down 2>/dev/null || true
    
    # Iniciar servicio principal
    docker-compose up -d paddleocr-enterprise
    
    # Esperar a que el servicio esté listo
    log "⏳ Esperando a que el servidor esté listo..."
    
    TIMEOUT=120
    COUNTER=0
    
    while [ $COUNTER -lt $TIMEOUT ]; do
        if curl -f http://localhost:8501/health &>/dev/null; then
            log "✅ Servidor OCR listo y operativo!"
            break
        fi
        
        echo -n "."
        sleep 2
        COUNTER=$((COUNTER + 2))
    done
    
    if [ $COUNTER -ge $TIMEOUT ]; then
        error "Timeout esperando al servidor. Revisa los logs: docker-compose logs"
    fi
}

# Verificar instalación
verify_installation() {
    log "🧪 Verificando instalación..."
    
    # Test básico de salud
    HEALTH_RESPONSE=$(curl -s http://localhost:8501/health)
    if echo "$HEALTH_RESPONSE" | grep -q '"ocr_ready": true'; then
        log "✅ Health check: OK"
    else
        warn "Health check falló. Respuesta: $HEALTH_RESPONSE"
    fi
    
    # Test de estadísticas
    if curl -f http://localhost:8501/stats &>/dev/null; then
        log "✅ Endpoint de estadísticas: OK"
    else
        warn "Endpoint de estadísticas no responde"
    fi
    
    # Mostrar información del contenedor
    info "📊 Estado del contenedor:"
    docker ps | grep ocr-server-enterprise || warn "Contenedor no encontrado"
    
    # Mostrar logs recientes
    info "📝 Logs recientes:"
    docker-compose logs --tail=5 paddleocr-enterprise
}

# Mostrar información final
show_final_info() {
    echo -e "${GREEN}"
    cat << "EOF"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    ✅ INSTALACIÓN COMPLETADA                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"
    
    info "🌐 Servidor disponible en: http://localhost:8501"
    info "📊 Dashboard: http://localhost:8501"
    info "🔍 Health Check: http://localhost:8501/health"
    info "📈 Estadísticas: http://localhost:8501/stats"
    
    echo -e "\n${YELLOW}📖 Comandos útiles:${NC}"
    echo "  • Ver logs:           docker-compose logs -f"
    echo "  • Reiniciar:          docker-compose restart"
    echo "  • Parar servicio:     docker-compose down"
    echo "  • Ver estadísticas:   curl http://localhost:8501/stats"
    echo "  • Test de archivo:    curl -X POST -F 'file=@test.pdf' http://localhost:8501/process"
    
    echo -e "\n${YELLOW}📂 Estructura de archivos:${NC}"
    echo "  • Archivos entrada:   ./data/input/"
    echo "  • Resultados:         ./data/output/"
    echo "  • Logs:               ./data/logs/"
    echo "  • Configuración:      ./config/"
    echo "  • Modelos OCR:        ./volumes/paddleocr-models/"
    
    echo -e "\n${GREEN}🎉 ¡OCR Server Empresarial listo para usar!${NC}"
}

# Función principal
main() {
    case "${1:-install}" in
        "install")
            log "🚀 Iniciando configuración empresarial completa..."
            check_requirements
            create_directory_structure
            build_docker_image
            setup_security
            start_service
            verify_installation
            show_final_info
            ;;
        "update")
            log "🔄 Actualizando OCR Server..."
            docker-compose down
            build_docker_image
            start_service
            verify_installation
            log "✅ Actualización completada"
            ;;
        "restart")
            log "🔄 Reiniciando servicio..."
            docker-compose restart
            verify_installation
            ;;
        "status")
            log "📊 Estado del sistema:"
            docker-compose ps
            verify_installation
            ;;
        "logs")
            log "📝 Mostrando logs..."
            docker-compose logs -f
            ;;
        "clean")
            log "🧹 Limpiando sistema..."
            docker-compose down
            docker system prune -f
            log "✅ Limpieza completada"
            ;;
        "help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  install  - Instalación completa (por defecto)"
            echo "  update   - Actualizar servidor"
            echo "  restart  - Reiniciar servicio"
            echo "  status   - Ver estado del sistema"
            echo "  logs     - Ver logs en tiempo real"
            echo "  clean    - Limpiar sistema Docker"
            echo "  help     - Mostrar esta ayuda"
            ;;
        *)
            error "Comando no reconocido: $1. Usa '$0 help' para ver comandos disponibles."
            ;;
    esac
}

# Ejecutar función principal
main "$@"