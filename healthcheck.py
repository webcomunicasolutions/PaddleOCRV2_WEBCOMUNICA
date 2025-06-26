#!/usr/bin/env python3
"""
Health Check Script para OCR Server Empresarial
Verifica que el servidor esté funcionando correctamente
"""

import sys
import requests
import time
import json

def check_health():
    """Verificar salud del servidor OCR"""
    try:
        # Intentar conectar al endpoint de health
        response = requests.get("http://localhost:8501/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            
            # Verificar que OCR esté listo
            if health_data.get("ocr_ready", False):
                print("✅ Health check: OCR Server healthy")
                return True
            else:
                print("❌ Health check: OCR not ready")
                return False
        else:
            print(f"❌ Health check: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Health check: Connection refused")
        return False
    except requests.exceptions.Timeout:
        print("❌ Health check: Timeout")
        return False
    except Exception as e:
        print(f"❌ Health check: Error - {e}")
        return False

def main():
    """Función principal"""
    print("🔍 Ejecutando health check...")
    
    if check_health():
        print("🎉 Servidor OCR funcionando correctamente")
        sys.exit(0)
    else:
        print("💥 Servidor OCR no está funcionando")
        sys.exit(1)

if __name__ == "__main__":
    main()