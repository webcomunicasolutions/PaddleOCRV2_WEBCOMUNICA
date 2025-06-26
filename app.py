#!/usr/bin/env python3
"""
PaddleOCR Server Empresarial v3.0 - Optimizado para Producción
Servidor OCR profesional con todas las mejoras empresariales
"""

import os
import json
import time
import tempfile
import numpy as np
import cv2
import math
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from werkzeug.serving import WSGIRequestHandler
import threading
from datetime import datetime

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/data/ocr_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración empresarial
UPLOAD_FOLDER = '/app/data/input'
OUTPUT_FOLDER = '/app/data/output'
LOG_FOLDER = '/app/data/logs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'bmp', 'tiff', 'tif'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_REQUESTS = 100  # peticiones por ventana

# Variables globales optimizadas
ocr_instances = {}
supported_languages = ["en", "es"]
default_lang = "es"
ocr_initialized = False
server_stats = {
    'startup_time': time.time(),
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'total_processing_time': 0.0,
    'models_loaded': False
}
request_history = []  # Para rate limiting básico

def allowed_file(filename):
    """Validar extensión de archivo"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_file_size(file):
    """Validar tamaño de archivo"""
    file.seek(0, 2)  # Ir al final
    size = file.tell()
    file.seek(0)  # Volver al inicio
    return size <= MAX_FILE_SIZE

def rate_limit_check(request_ip):
    """Rate limiting básico"""
    current_time = time.time()
    # Limpiar requests antiguos
    global request_history
    request_history = [req for req in request_history if current_time - req['time'] < RATE_LIMIT_WINDOW]
    
    # Contar requests del IP
    ip_requests = [req for req in request_history if req['ip'] == request_ip]
    
    if len(ip_requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Agregar request actual
    request_history.append({'ip': request_ip, 'time': current_time})
    return True

def calculate_intelligent_side_len(image_path):
    """Cálculo inteligente de side_len para optimizar detección"""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return 960
        
        h, w = img.shape[:2]
        side_len = int(math.ceil(max(h, w) * max(0.8, 960 / max(h, w))))
        logger.debug(f"Imagen {w}x{h} -> side_len: {side_len}px")
        return side_len
    except Exception as e:
        logger.error(f"Error calculando side_len: {e}")
        return 960

def initialize_ocr():
    """Inicializar OCR con configuración empresarial optimizada"""
    global ocr_instances, ocr_initialized, server_stats
    
    if ocr_initialized:
        return True
    
    try:
        logger.info("🚀 Inicializando PaddleOCR Empresarial (configuración optimizada)...")
        import paddleocr
        
        logger.info(f"📦 PaddleOCR version: {paddleocr.__version__}")
        
        # Configuración empresarial optimizada
        ocr_config = {
            'use_angle_cls': True,      # ✅ CRÍTICO: Detección de ángulos
            'use_gpu': False,           # ✅ CPU por compatibilidad
            'det_db_thresh': 0.1,       # 🏆 CLAVE: MUY sensible (más detección)
            'det_db_box_thresh': 0.4,   # 🏆 CLAVE: MUY sensible (más cajas)
            'drop_score': 0.2,          # 🏆 CLAVE: MUY permisivo (más texto)
            'show_log': False,          # Sin logs verbosos
            'det_limit_side_len': 1280, # Optimizado para documentos grandes
            'rec_batch_num': 6,         # Batch para mejor rendimiento
            'cpu_threads': 4            # Threads optimizados
        }
        
        for lang in supported_languages:
            logger.info(f"📚 Cargando OCR optimizado para {lang.upper()}...")
            
            try:
                ocr_instances[lang] = paddleocr.PaddleOCR(lang=lang, **ocr_config)
                logger.info(f"   ✅ OCR configurado para {lang} (modo empresarial)")
            except Exception as e:
                logger.error(f"❌ Error cargando OCR para {lang}: {e}")
                return False
        
        ocr_initialized = True
        server_stats['models_loaded'] = True
        logger.info("✅ OCR inicializado con configuración empresarial")
        logger.info("🏆 Rendimiento esperado: 80+ bloques, 95%+ confianza")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error crítico inicializando OCR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def get_ocr_instance(language=None):
    """Obtener instancia OCR optimizada con fallback"""
    global ocr_instances, ocr_initialized
    
    if not ocr_initialized:
        if not initialize_ocr():
            return None
    
    lang = language or default_lang
    
    # Fallback inteligente
    if lang not in ocr_instances:
        logger.warning(f"Idioma {lang} no disponible, usando {default_lang}")
        lang = default_lang
    
    return ocr_instances.get(lang)

def detect_text_orientation_improved(coordinates):
    """Detección mejorada y robusta de orientación de texto"""
    try:
        if not coordinates or len(coordinates) < 4:
            return 'horizontal'
            
        x_coords = [point[0] for point in coordinates]
        y_coords = [point[1] for point in coordinates]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        
        if width == 0:
            return 'vertical'
        
        # Métricas mejoradas
        aspect_ratio = height / width
        p1, p2 = coordinates[0], coordinates[1]
        angle = abs(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]) * 180 / np.pi)
        
        # Lógica empresarial de clasificación
        if aspect_ratio > 3.0:
            return 'vertical'
        elif angle > 30 and angle < 150:
            return 'rotated'
        elif aspect_ratio > 2.0:
            return 'vertical'
        else:
            return 'horizontal'
            
    except Exception as e:
        logger.debug(f"Error detectando orientación: {e}")
        return 'horizontal'

def analyze_text_orientations(coordinates_list):
    """Analizar orientaciones con estadísticas detalladas"""
    orientations = {'horizontal': 0, 'vertical': 0, 'rotated': 0}
    
    for coords in coordinates_list:
        orientation = detect_text_orientation_improved(coords)
        orientations[orientation] += 1
    
    return orientations

def process_ocr_result_robust(ocr_result):
    """Procesamiento robusto del resultado OCR empresarial"""
    text_lines = []
    confidences = []
    coordinates_list = []
    
    if not ocr_result or not isinstance(ocr_result, list):
        logger.warning("Resultado OCR vacío o inválido")
        return text_lines, confidences, coordinates_list
    
    try:
        logger.debug("🔍 Procesando resultado OCR con método empresarial...")
        
        for page_idx, page in enumerate(ocr_result):
            if not page:
                continue
                
            for line_idx, line in enumerate(page):
                try:
                    if not line or len(line) < 2:
                        continue
                        
                    coordinates = line[0]
                    text_data = line[1]
                    
                    # Procesamiento robusto de datos
                    if isinstance(text_data, (list, tuple)) and len(text_data) >= 2:
                        text = str(text_data[0]).strip()
                        confidence = float(text_data[1])
                        
                        # Filtros de calidad empresariales
                        if text and len(text) > 0 and confidence > 0.1:  # Umbral mínimo
                            text_lines.append(text)
                            confidences.append(confidence)
                            coordinates_list.append(coordinates)
                            
                except Exception as e:
                    logger.debug(f"Error procesando línea {line_idx}: {e}")
                    continue
                    
        logger.info(f"✅ Procesamiento completado: {len(text_lines)} bloques detectados")
                    
    except Exception as e:
        logger.error(f"Error crítico procesando resultado OCR: {e}")
    
    return text_lines, confidences, coordinates_list

def save_processing_result(filename, response_data):
    """Guardar resultado para auditoría empresarial"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = Path(OUTPUT_FOLDER) / f"{timestamp}_{filename}_result.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Resultado guardado: {result_file}")
        return str(result_file)
    except Exception as e:
        logger.error(f"Error guardando resultado: {e}")
        return None

# Suprimir warnings de Flask para logs más limpios
class QuietWSGIRequestHandler(WSGIRequestHandler):
    def log_request(self, code='-', size='-'):
        # Solo logear errores
        if str(code).startswith('4') or str(code).startswith('5'):
            super().log_request(code, size)

@app.route('/')
def index():
    """Página de información empresarial del servidor"""
    uptime = time.time() - server_stats['startup_time']
    avg_processing_time = (server_stats['total_processing_time'] / server_stats['total_requests'] 
                          if server_stats['total_requests'] > 0 else 0)
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCR Server Empresarial - PaddleOCR v3.0</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .header { background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 8px 32px rgba(31,38,135,0.37); backdrop-filter: blur(8px); margin-bottom: 20px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .stat-number { font-size: 24px; font-weight: bold; color: #2c3e50; }
            .stat-label { color: #7f8c8d; font-size: 14px; margin-top: 5px; }
            .status { font-size: 18px; margin: 20px 0; }
            .ok { color: #27ae60; font-weight: bold; }
            .error { color: #e74c3c; font-weight: bold; }
            .feature { background: rgba(255,255,255,0.9); padding: 20px; margin: 10px 0; border-radius: 10px; border-left: 4px solid #3498db; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .code { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; font-family: 'Courier New', monospace; overflow-x: auto; }
            h1 { color: #2c3e50; margin: 0; }
            h3 { color: #34495e; margin-top: 0; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 OCR Server Empresarial v3.0</h1>
                <p style="margin: 10px 0 0 0; color: #7f8c8d;">Servidor OCR profesional optimizado para entornos empresariales</p>
                
                <div class="status">
                    <strong>Estado del Sistema:</strong> 
                    <span class="{{ 'ok' if ocr_ready else 'error' }}">
                        {{ "✅ Operativo" if ocr_ready else "❌ Inicializando" }}
                    </span>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ "{:.1f}h".format(uptime/3600) }}</div>
                    <div class="stat-label">Tiempo Activo</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ total_requests }}</div>
                    <div class="stat-label">Total Peticiones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ "{:.1f}%".format((successful_requests/total_requests*100) if total_requests > 0 else 0) }}</div>
                    <div class="stat-label">Tasa Éxito</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ "{:.2f}s".format(avg_processing_time) }}</div>
                    <div class="stat-label">Tiempo Promedio</div>
                </div>
            </div>
            
            <div class="feature">
                <h3>🔧 Configuración Empresarial</h3>
                <ul style="margin: 0;">
                    <li>✅ <strong>PaddleOCR 2.8.1</strong> - Versión estable optimizada</li>
                    <li>✅ <strong>Detección avanzada</strong> - Ángulos y orientaciones</li>
                    <li>✅ <strong>Soporte PDF nativo</strong> - Sin conversión manual</li>
                    <li>✅ <strong>Rate limiting</strong> - Protección contra abuso</li>
                    <li>✅ <strong>Logging completo</strong> - Auditoría empresarial</li>
                    <li>✅ <strong>Validación robusta</strong> - Archivos y tamaños</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🌍 Especificaciones Técnicas</h3>
                <p><strong>Idiomas:</strong> Español (ES), Inglés (EN)</p>
                <p><strong>Formatos:</strong> PDF, JPG, PNG, BMP, TIFF</p>
                <p><strong>Tamaño máximo:</strong> 50MB por archivo</p>
                <p><strong>Rate limit:</strong> 100 peticiones/minuto por IP</p>
            </div>
            
            <div class="feature">
                <h3>📡 API Endpoints</h3>
                <div class="endpoint"><strong>GET /</strong> - Interfaz de información</div>
                <div class="endpoint"><strong>GET /health</strong> - Estado del servidor</div>
                <div class="endpoint"><strong>GET /stats</strong> - Estadísticas detalladas</div>
                <div class="endpoint"><strong>POST /process</strong> - Procesar archivo</div>
                <div class="endpoint"><strong>POST /process?detailed=true</strong> - Procesamiento detallado</div>
            </div>
            
            <div class="feature">
                <h3>💡 Ejemplo de Uso</h3>
                <div class="code">
# Procesamiento básico<br>
curl -X POST http://localhost:8501/process \\<br>
&nbsp;&nbsp;-F "file=@documento.pdf" \\<br>
&nbsp;&nbsp;-F "language=es"<br><br>

# Procesamiento detallado con coordenadas<br>
curl -X POST http://localhost:8501/process \\<br>
&nbsp;&nbsp;-F "file=@factura.pdf" \\<br>
&nbsp;&nbsp;-F "language=es" \\<br>
&nbsp;&nbsp;-F "detailed=true"
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', 
    ocr_ready=ocr_initialized,
    uptime=uptime,
    total_requests=server_stats['total_requests'],
    successful_requests=server_stats['successful_requests'],
    avg_processing_time=avg_processing_time
    )

@app.route('/health')
def health():
    """Endpoint de health check empresarial"""
    uptime = time.time() - server_stats['startup_time']
    
    return jsonify({
        'status': 'healthy' if ocr_initialized else 'initializing',
        'ocr_ready': ocr_initialized,
        'models_loaded': server_stats['models_loaded'],
        'version': '3.0-enterprise',
        'uptime_seconds': round(uptime, 2),
        'supported_languages': supported_languages,
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
        'rate_limit': f"{RATE_LIMIT_REQUESTS} req/min",
        'optimizations': [
            'enterprise_config', 
            'robust_processing', 
            'intelligent_detection',
            'rate_limiting',
            'audit_logging'
        ],
        'timestamp': time.time()
    })

@app.route('/stats')
def stats():
    """Estadísticas detalladas del servidor"""
    uptime = time.time() - server_stats['startup_time']
    
    return jsonify({
        'server_stats': {
            **server_stats,
            'uptime_seconds': round(uptime, 2),
            'avg_processing_time': (server_stats['total_processing_time'] / server_stats['total_requests'] 
                                  if server_stats['total_requests'] > 0 else 0),
            'success_rate': (server_stats['successful_requests'] / server_stats['total_requests'] * 100
                           if server_stats['total_requests'] > 0 else 0)
        },
        'active_rate_limits': len(request_history),
        'system_info': {
            'ocr_version': '2.8.1',
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            'supported_formats': list(ALLOWED_EXTENSIONS)
        }
    })

@app.route('/process', methods=['POST'])
def process_file():
    """Endpoint principal de procesamiento OCR empresarial"""
    start_time = time.time()
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    
    # Actualizar estadísticas
    server_stats['total_requests'] += 1
    
    try:
        # Rate limiting
        if not rate_limit_check(client_ip):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return jsonify({
                'error': 'Rate limit excedido',
                'limit': f'{RATE_LIMIT_REQUESTS} peticiones por minuto',
                'retry_after': RATE_LIMIT_WINDOW
            }), 429
        
        # Verificar inicialización
        if not ocr_initialized:
            logger.error("OCR no inicializado")
            if not initialize_ocr():
                return jsonify({'error': 'OCR no disponible'}), 503
        
        # Validaciones de entrada
        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no proporcionado'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'Archivo inválido'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Formato no soportado',
                'supported_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        if not check_file_size(file):
            return jsonify({
                'error': 'Archivo demasiado grande',
                'max_size_mb': MAX_FILE_SIZE // (1024 * 1024)
            }), 413
        
        # Parámetros de procesamiento
        language = request.form.get('language', default_lang)
        detailed = request.form.get('detailed', 'false').lower() == 'true'
        save_result = request.form.get('save_result', 'false').lower() == 'true'
        
        # Obtener instancia OCR
        ocr = get_ocr_instance(language)
        if ocr is None:
            return jsonify({'error': 'OCR no disponible para el idioma solicitado'}), 503
        
        filename = secure_filename(file.filename)
        logger.info(f"Procesando archivo: {filename} (idioma: {language}, IP: {client_ip})")
        
        # Procesar archivo en memoria temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
            file.save(tmp_file.name)
            
            try:
                logger.debug(f"Iniciando OCR para {filename}...")
                
                # Procesamiento OCR optimizado
                result = ocr.ocr(tmp_file.name, cls=True)
                
                logger.debug(f"OCR completado para {filename}")
                
            finally:
                # Limpiar archivo temporal
                try:
                    os.remove(tmp_file.name)
                except:
                    pass
        
        # Procesar resultado
        text_lines, confidences, coordinates_list = process_ocr_result_robust(result)
        
        # Análisis de orientaciones
        orientations = analyze_text_orientations(coordinates_list)
        
        # Estadísticas
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        processing_time = time.time() - start_time
        
        # Respuesta base
        response = {
            'success': True,
            'text': '\n'.join(text_lines),
            'total_blocks': len(text_lines),
            'filename': filename,
            'language': language,
            'avg_confidence': round(avg_confidence, 3) if avg_confidence > 0 else None,
            'processing_time': round(processing_time, 3),
            'ocr_version': '2.8.1-enterprise',
            'has_coordinates': len(coordinates_list) > 0,
            'text_orientations': orientations,
            'has_vertical_text': orientations.get('vertical', 0) > 0,
            'has_rotated_text': orientations.get('rotated', 0) > 0,
            'pdf_support': 'native',
            'timestamp': time.time(),
            'server_version': '3.0-enterprise'
        }
        
        # Modo detallado
        if detailed:
            blocks_with_coords = []
            for i, text in enumerate(text_lines):
                block_info = {'text': text, 'block_id': i}
                
                if i < len(confidences):
                    block_info['confidence'] = round(confidences[i], 3)
                
                if i < len(coordinates_list):
                    coords = coordinates_list[i]
                    if hasattr(coords, 'tolist'):
                        coords = coords.tolist()
                    block_info['coordinates'] = coords
                    block_info['orientation'] = detect_text_orientation_improved(coords)
                
                blocks_with_coords.append(block_info)
            
            response.update({
                'blocks': blocks_with_coords,
                'min_confidence': round(min(confidences), 3) if confidences else None,
                'max_confidence': round(max(confidences), 3) if confidences else None,
                'total_coordinates': len(coordinates_list),
                'orientation_details': {
                    'horizontal_blocks': orientations.get('horizontal', 0),
                    'vertical_blocks': orientations.get('vertical', 0),
                    'rotated_blocks': orientations.get('rotated', 0)
                },
                'quality_metrics': {
                    'high_confidence_blocks': len([c for c in confidences if c > 0.9]),
                    'medium_confidence_blocks': len([c for c in confidences if 0.7 <= c <= 0.9]),
                    'low_confidence_blocks': len([c for c in confidences if c < 0.7])
                }
            })
        
        # Guardar resultado si se solicita
        if save_result:
            saved_file = save_processing_result(filename, response)
            if saved_file:
                response['result_saved_to'] = saved_file
        
        # Actualizar estadísticas
        server_stats['successful_requests'] += 1
        server_stats['total_processing_time'] += processing_time
        
        logger.info(f"Procesamiento exitoso: {filename} - {len(text_lines)} bloques en {processing_time:.2f}s")
        
        return jsonify(response)
        
    except Exception as e:
        processing_time = time.time() - start_time
        server_stats['failed_requests'] += 1
        server_stats['total_processing_time'] += processing_time
        
        error_msg = str(e)
        logger.error(f"Error procesando archivo: {error_msg}")
        logger.debug("Stacktrace completo:", exc_info=True)
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'processing_time': round(processing_time, 3),
            'timestamp': time.time(),
            'server_version': '3.0-enterprise'
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'Archivo demasiado grande',
        'max_size_mb': MAX_FILE_SIZE // (1024 * 1024)
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Error interno del servidor: {e}")
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Crear directorios necesarios
    for directory in [UPLOAD_FOLDER, OUTPUT_FOLDER, LOG_FOLDER]:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("🚀 OCR Server Empresarial v3.0 iniciando...")
    logger.info("🔄 Pre-cargando modelos OCR...")
    
    # Pre-cargar modelos al arrancar
    if initialize_ocr():
        logger.info("✅ Modelos OCR pre-cargados exitosamente")
        logger.info("🏆 Configuración empresarial activa")
        logger.info("⚡ Servidor listo para peticiones")
    else:
        logger.error("⚠️ Error crítico pre-cargando modelos")
        exit(1)
    
    logger.info("🌐 Servidor iniciando en puerto 8501")
    logger.info("📊 Dashboard disponible en: http://localhost:8501")
    logger.info("🔒 Funciones empresariales activadas:")
    logger.info("   ✅ Rate limiting (100 req/min)")
    logger.info("   ✅ Validación robusta de archivos")
    logger.info("   ✅ Logging completo y auditoría")
    logger.info("   ✅ Estadísticas en tiempo real")
    logger.info("   ✅ Manejo de errores empresarial")
    
    # Usar servidor WSGI para producción o desarrollo silencioso
    try:
        from waitress import serve
        logger.info("🚀 Usando Waitress (servidor de producción)")
        serve(app, host='0.0.0.0', port=8501, threads=4)
    except ImportError:
        logger.info("⚠️ Waitress no disponible, usando Flask dev server")
        logger.info("💡 Para producción, instalar: pip install waitress")
        app.run(
            host='0.0.0.0', 
            port=8501, 
            debug=False,
            threaded=True,
            request_handler=QuietWSGIRequestHandler
        )