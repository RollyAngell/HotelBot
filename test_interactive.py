#!/usr/bin/env python3
"""
Pruebas interactivas del HotelBot
Permite probar el bot paso a paso como un usuario real
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class InteractiveBotTester:
    """Tester interactivo para el HotelBot"""
    
    def __init__(self):
        self.bot_username = None
        self.setup_info()
    
    def setup_info(self):
        """Mostrar información de configuración"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if token:
            # Extraer bot ID del token para generar username probable
            bot_id = token.split(':')[0]
            print(f"🤖 Bot ID: {bot_id}")
            print(f"🔗 Busca tu bot en Telegram (probablemente @tu_bot_name)")
        
        authorized_users = os.getenv('AUTHORIZED_USERS', '')
        if authorized_users:
            users = [u.strip() for u in authorized_users.split(',') if u.strip()]
            print(f"👥 Usuarios autorizados: {len(users)}")
            print(f"   IDs: {', '.join(users)}")
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        print("\n" + "="*60)
        print("🧪 PRUEBAS INTERACTIVAS - HOTELBOT")
        print("="*60)
        print("Elige qué quieres probar:")
        print()
        print("1. 📱 Guía para probar en Telegram")
        print("2. 🔧 Ejecutar pruebas técnicas")
        print("3. 📊 Verificar configuración")
        print("4. 🎯 Checklist de funcionalidades")
        print("5. 📸 Consejos para fotos de DNI")
        print("6. 🚀 Guía de deployment")
        print("0. ❌ Salir")
        print("-"*60)
    
    def telegram_guide(self):
        """Guía para probar en Telegram"""
        print("\n📱 GUÍA PASO A PASO - PRUEBAS EN TELEGRAM")
        print("="*50)
        
        print("\n🔍 PASO 1: Encontrar tu bot")
        print(f"   • Abre Telegram")
        print(f"   • Busca tu bot (revisa el nombre que le diste)")
        print(f"   • O busca por el ID del token si lo recuerdas")
        
        print("\n🚀 PASO 2: Comandos básicos")
        print("   • Envía: /start")
        print("   • Deberías ver el mensaje de bienvenida")
        print("   • Si ves 'No tienes autorización', verifica AUTHORIZED_USERS")
        
        print("\n📝 PASO 3: Registro completo")
        print("   • Envía: /nuevo")
        print("   • Toma una foto de un DNI (puede ser el tuyo)")
        print("   • Espera 10-20 segundos (procesamiento OCR)")
        print("   • Sigue las instrucciones del bot")
        print("   • Completa: duración → precio → pago → habitación → observaciones")
        print("   • Confirma el registro")
        
        print("\n📊 PASO 4: Reportes")
        print("   • Envía: /resumen")
        print("   • Envía: /habitaciones")
        print("   • Envía: /ayuda")
        
        print("\n✅ PASO 5: Verificar resultados")
        print("   • Abre tu Google Sheet - debería tener una nueva fila")
        print("   • Abre tu carpeta de Google Drive - debería tener la foto")
        
        print("\n💡 CONSEJOS:")
        print("   • Si OCR falla, usa la opción 'Editar datos' para corregir")
        print("   • Si bot no responde, revisa los logs en la terminal")
        print("   • El bot es robusto y manejará diferentes fotos automáticamente")
        
        input("\n📱 Presiona Enter cuando hayas completado las pruebas en Telegram...")
    
    def run_technical_tests(self):
        """Ejecutar pruebas técnicas"""
        print("\n🔧 EJECUTANDO PRUEBAS TÉCNICAS...")
        print("-"*40)
        
        # Preguntar qué tipo de pruebas ejecutar
        print("¿Qué pruebas quieres ejecutar?")
        print("1. 🔧 Pruebas de configuración (rápidas)")
        print("2. 🚀 Pruebas funcionales completas (pueden tardar)")
        print("3. 🎯 Ambas")
        
        choice = input("\nSelecciona (1-3): ").strip()
        
        if choice in ['1', '3']:
            print("\n🔧 Ejecutando pruebas de configuración...")
            os.system("python test_bot.py")
            
        if choice in ['2', '3']:
            print("\n🚀 Ejecutando pruebas funcionales completas...")
            if Path("test_bot_functional.py").exists():
                os.system("python test_bot_functional.py")
            else:
                print("❌ test_bot_functional.py no encontrado")
        
        input("\n📊 Presiona Enter para continuar...")
    
    def check_configuration(self):
        """Verificar configuración"""
        print("\n📊 VERIFICACIÓN DE CONFIGURACIÓN")
        print("="*40)
        
        # Variables de entorno
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'OPENAI_API_KEY', 
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_SHEETS_SPREADSHEET_ID',
            'GOOGLE_DRIVE_FOLDER_ID'
        ]
        
        print("\n🔧 Variables de entorno:")
        all_configured = True
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mostrar solo primeros y últimos caracteres
                if len(value) > 10:
                    display = f"{value[:4]}...{value[-4:]}"
                else:
                    display = "***"
                print(f"   ✅ {var}: {display}")
            else:
                print(f"   ❌ {var}: No configurada")
                all_configured = False
        
        # Archivos de credenciales
        print("\n📁 Archivos de credenciales:")
        creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_file and Path(creds_file).exists():
            print(f"   ✅ {creds_file}: Existe")
        else:
            print(f"   ❌ {creds_file}: No encontrado")
            all_configured = False
        
        oauth_file = os.getenv('GOOGLE_OAUTH_CREDENTIALS', 'credentials/credentials.json')
        if Path(oauth_file).exists():
            print(f"   ✅ {oauth_file}: Existe")
        else:
            print(f"   ⚠️  {oauth_file}: No encontrado (se creará al usar el bot)")
        
        # Dependencias
        print("\n📦 Verificando dependencias críticas:")
        deps = ['telegram', 'openai', 'gspread', 'PIL']
        for dep in deps:
            try:
                __import__(dep)
                print(f"   ✅ {dep}: Instalado")
            except ImportError:
                print(f"   ❌ {dep}: No instalado")
                all_configured = False
        
        if all_configured:
            print("\n🎉 ¡Configuración completa!")
        else:
            print("\n⚠️  Configuración incompleta - revisa los elementos marcados")
        
        input("\n📊 Presiona Enter para continuar...")
    
    def functionality_checklist(self):
        """Checklist de funcionalidades"""
        print("\n🎯 CHECKLIST DE FUNCIONALIDADES")
        print("="*45)
        
        checklist = [
            ("📱 Bot responde a /start", "Mensaje de bienvenida con comandos"),
            ("🔒 Control de acceso", "Solo usuarios autorizados pueden usarlo"),
            ("📝 Comando /nuevo", "Inicia proceso de registro"),
            ("📸 Procesamiento OCR", "Extrae datos del DNI automáticamente"),
            ("📋 Formulario guiado", "Duración → Precio → Pago → Habitación"),
            ("💾 Guardado en Sheets", "Nueva fila con todos los datos"),
            ("📁 Subida a Drive", "Foto del DNI con nombre único"),
            ("📊 Comando /resumen", "Total clientes e ingresos del día"),
            ("🏠 Comando /habitaciones", "Disponibilidad actualizada"),
            ("❓ Comando /ayuda", "Manual completo del bot"),
            ("⚙️ Opciones personalizadas", "Precio y habitación custom"),
            ("✏️ Edición de datos", "Corregir datos extraídos por OCR"),
            ("🔄 Manejo de errores", "Fotos inválidas, usuarios no autorizados"),
            ("🚀 Rendimiento", "OCR en menos de 20 segundos")
        ]
        
        print("\nMarca cada funcionalidad que hayas probado exitosamente:")
        print("(Usa las pruebas en Telegram para verificar)")
        print()
        
        checked = 0
        for i, (item, description) in enumerate(checklist, 1):
            print(f"{i:2d}. {item}")
            print(f"    📝 {description}")
            
            result = input("    ✅ ¿Funciona? (s/n): ").lower().strip()
            if result in ['s', 'si', 'sí', 'y', 'yes']:
                checked += 1
                print("    ✅ Marcado como funcional")
            else:
                print("    ❌ Marcado como no funcional")
            print()
        
        success_rate = (checked / len(checklist)) * 100
        
        print("="*45)
        print(f"📊 RESULTADO FINAL")
        print(f"✅ Funcionales: {checked}/{len(checklist)}")
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 ¡EXCELENTE! Tu bot está listo para producción")
        elif success_rate >= 70:
            print("👍 ¡BUENO! El bot funciona bien, algunos ajustes menores")
        elif success_rate >= 50:
            print("⚠️  REGULAR - Necesitas revisar varias funcionalidades")
        else:
            print("❌ CRÍTICO - Muchas funcionalidades no están trabajando")
        
        input("\n📊 Presiona Enter para continuar...")
    
    def dni_photo_tips(self):
        """Consejos para fotos de DNI"""
        print("\n📸 CONSEJOS PARA FOTOS DE DNI")
        print("="*40)
        
        print("\n✅ FOTOS QUE FUNCIONAN BIEN:")
        print("   • Frontal y centrado")
        print("   • Buena iluminación (luz natural preferible)")
        print("   • Texto claramente visible")
        print("   • Contraste adecuado")
        print("   • Tamaño de archivo < 10MB")
        
        print("\n⚠️  FOTOS QUE PUEDEN DAR PROBLEMAS:")
        print("   • Muy borrosas o fuera de foco")
        print("   • Demasiado oscuras")
        print("   • Ángulos muy extremos")
        print("   • Reflejos que oculten texto")
        print("   • Archivos muy pesados (>20MB)")
        
        print("\n🔧 SI EL OCR FALLA:")
        print("   1. Toma otra foto más nítida")
        print("   2. Mejora la iluminación")
        print("   3. Asegúrate de que el texto sea legible")
        print("   4. Usa la opción 'Editar datos' para corregir")
        
        print("\n🌍 DOCUMENTOS SOPORTADOS:")
        print("   • DNI Peruano (8 dígitos)")
        print("   • Cédula Venezolana (V- o E-)")
        print("   • Cédula Colombiana")
        print("   • Otros documentos latinoamericanos")
        
        print("\n💡 TIP AVANZADO:")
        print("   El bot usa múltiples métodos de extracción automáticamente.")
        print("   Si una foto no da buenos resultados, el sistema")
        print("   intentará mejorarla y procesarla de diferentes formas.")
        
        input("\n📸 Presiona Enter para continuar...")
    
    def deployment_guide(self):
        """Guía de deployment"""
        print("\n🚀 GUÍA DE DEPLOYMENT")
        print("="*30)
        
        print("\n📋 ANTES DE HACER DEPLOYMENT:")
        print("   ✅ Todas las pruebas pasan")
        print("   ✅ Bot funciona correctamente en local")
        print("   ✅ Variables de entorno configuradas")
        print("   ✅ Personal capacitado en el uso")
        
        print("\n🌐 OPCIONES DE DEPLOYMENT:")
        
        print("\n1. 🚂 RAILWAY (Recomendado)")
        print("   • Gratis hasta cierto uso")
        print("   • Deploy automático desde GitHub")
        print("   • Variables de entorno fáciles de configurar")
        print("   • Logs en tiempo real")
        
        print("\n2. 💜 HEROKU")
        print("   • Opción clásica y confiable") 
        print("   • Dynos gratuitos limitados")
        print("   • Buildpacks automáticos")
        print("   • Add-ons para monitoreo")
        
        print("\n3. 🌊 DIGITALOCEAN/LINODE (VPS)")
        print("   • Máximo control")
        print("   • Más económico a largo plazo")
        print("   • Requiere conocimientos de servidor")
        print("   • Usar systemd para mantener el bot corriendo")
        
        print("\n📦 ARCHIVOS NECESARIOS PARA DEPLOYMENT:")
        print("   • requirements.txt ✅")
        print("   • Procfile (para Heroku)")
        print("   • railway.toml (para Railway)")  
        print("   • Archivos de credenciales")
        print("   • Variables de entorno")
        
        print("\n🔧 CONFIGURACIÓN POST-DEPLOYMENT:")
        print("   • Configurar variables de entorno en la plataforma")
        print("   • Subir credenciales de Google de forma segura")
        print("   • Configurar logs y monitoreo")
        print("   • Probar funcionalidad completa")
        print("   • Capacitar al equipo")
        
        print("\n📊 MONITOREO EN PRODUCCIÓN:")
        print("   • Revisar logs regularmente")
        print("   • Verificar uso de créditos OpenAI")
        print("   • Monitorear espacio en Google Drive")
        print("   • Backup periódico de Google Sheets")
        
        input("\n🚀 Presiona Enter para continuar...")
    
    def run(self):
        """Ejecutar tester interactivo"""
        while True:
            self.show_main_menu()
            
            choice = input("\nSelecciona una opción (0-6): ").strip()
            
            if choice == '0':
                print("\n👋 ¡Hasta luego! Tu HotelBot está listo para la acción.")
                break
            elif choice == '1':
                self.telegram_guide()
            elif choice == '2':
                self.run_technical_tests()
            elif choice == '3':
                self.check_configuration()
            elif choice == '4':
                self.functionality_checklist()
            elif choice == '5':
                self.dni_photo_tips()
            elif choice == '6':
                self.deployment_guide()
            else:
                print("❌ Opción inválida. Selecciona 0-6.")
                time.sleep(1)

def main():
    """Función principal"""
    try:
        tester = InteractiveBotTester()
        tester.run()
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 ¡Adiós!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 