#!/usr/bin/env python3
"""
Script de inicio para el Bot de Hotel
Verifica la configuración antes de iniciar el bot
"""

import os
import sys
import logging
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    required_modules = [
        'telegram',
        'openai',
        'gspread',
        'PIL',
        'dotenv',
        'pytz'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Faltan las siguientes dependencias:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\n📦 Instala las dependencias con:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Verificar variables de entorno"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_SHEETS_SPREADSHEET_ID',
        'GOOGLE_DRIVE_FOLDER_ID'
    ]
    
    missing_vars = []
    
    # Cargar archivo .env si existe
    env_file = Path('.env')
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Archivo .env cargado")
    else:
        print("⚠️  Archivo .env no encontrado")
        print("📝 Crea un archivo .env basado en config_example.env")
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Faltan las siguientes variables de entorno:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    return True

def check_credentials():
    """Verificar archivo de credenciales"""
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not credentials_path:
        print("❌ Variable GOOGLE_APPLICATION_CREDENTIALS no configurada")
        return False
    
    if not Path(credentials_path).exists():
        print(f"❌ Archivo de credenciales no encontrado: {credentials_path}")
        print("📝 Descarga el archivo desde Google Cloud Console")
        return False
    
    return True

def check_authorized_users():
    """Verificar usuarios autorizados"""
    authorized_users = os.getenv('AUTHORIZED_USERS', '')
    
    if not authorized_users:
        print("⚠️  No hay usuarios autorizados configurados")
        print("📝 Configura AUTHORIZED_USERS en el archivo .env")
        return False
    
    try:
        user_list = [int(user.strip()) for user in authorized_users.split(',') if user.strip()]
        print(f"✅ {len(user_list)} usuario(s) autorizado(s)")
        return True
    except ValueError:
        print("❌ Error en formato de AUTHORIZED_USERS")
        print("📝 Debe ser una lista de números separados por comas")
        return False

def main():
    """Función principal"""
    print("🏨 Bot de Registro de Clientes - Hotel")
    print("=" * 50)
    
    print("\n🔍 Verificando configuración...")
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ Todas las dependencias están instaladas")
    
    # Verificar variables de entorno
    print("\n🔧 Verificando variables de entorno...")
    if not check_environment():
        sys.exit(1)
    print("✅ Variables de entorno configuradas")
    
    # Verificar credenciales
    print("\n🔐 Verificando credenciales...")
    if not check_credentials():
        sys.exit(1)
    print("✅ Archivo de credenciales encontrado")
    
    # Verificar usuarios autorizados
    print("\n👥 Verificando usuarios autorizados...")
    if not check_authorized_users():
        sys.exit(1)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n✅ Configuración verificada exitosamente")
    print("🚀 Iniciando bot...")
    print("-" * 50)
    
    try:
        # Importar y ejecutar el bot
        from hotel_bot import HotelBot
        
        bot = HotelBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el bot: {str(e)}")
        logging.error(f"Error al iniciar el bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 