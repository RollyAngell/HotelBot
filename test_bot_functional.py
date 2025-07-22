#!/usr/bin/env python3
"""
Pruebas funcionales completas para HotelBot
Simula un usuario real interactuando con el bot de Telegram
"""

import os
import sys
import time
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TEST-FUNC] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotFunctionalTester:
    """Tester funcional completo del HotelBot"""
    
    def __init__(self):
        self.bot = None
        self.test_results = {
            'passed': 0,
            'failed': 0, 
            'total': 0,
            'details': []
        }
        
        # Cargar configuración
        from dotenv import load_dotenv
        load_dotenv()
        
    def setup_bot(self):
        """Configurar instancia del bot para pruebas"""
        try:
            from hotel_bot import HotelBot
            self.bot = HotelBot()
            logger.info("✅ Bot inicializado para pruebas")
            return True
        except Exception as e:
            logger.error(f"❌ Error al inicializar bot: {e}")
            return False
    
    def create_test_image(self):
        """Crear imagen de prueba que simula un DNI"""
        try:
            # Crear imagen de prueba con texto simulando DNI
            img = Image.new('RGB', (600, 400), color='white')
            
            # Simular texto de DNI (esto es solo para pruebas, no será procesado por OCR real)
            # En pruebas reales necesitarías una imagen real de DNI
            
            # Guardar imagen temporal
            test_image_path = Path("test_dni_image.jpg")
            img.save(test_image_path, "JPEG")
            
            # Leer bytes de la imagen
            with open(test_image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Limpiar archivo temporal
            test_image_path.unlink()
            
            logger.info("✅ Imagen de prueba creada")
            return image_bytes
            
        except Exception as e:
            logger.error(f"❌ Error creando imagen de prueba: {e}")
            return None
    
    def test_ocr_processing(self):
        """Probar procesamiento OCR directamente"""
        logger.info("🧪 Probando procesamiento OCR...")
        self.test_results['total'] += 1
        
        try:
            from utils.ocr_processor import OCRProcessor
            
            ocr = OCRProcessor()
            
            # Usar imagen de prueba
            test_image = self.create_test_image()
            if not test_image:
                raise Exception("No se pudo crear imagen de prueba")
            
            # Procesar OCR (esto hará una llamada real a OpenAI)
            logger.info("   Procesando imagen con OpenAI Vision...")
            extracted_text = ocr.extract_text_from_image(test_image)
            
            if extracted_text and len(extracted_text) > 10:
                logger.info(f"✅ OCR procesó imagen correctamente ({len(extracted_text)} caracteres)")
                
                # Probar extracción de datos estructurados
                dni_data = ocr.extract_dni_data(extracted_text)
                logger.info(f"   Datos extraídos: {dni_data}")
                
                self.test_results['passed'] += 1
                self.test_results['details'].append({
                    'test': 'OCR Processing',
                    'status': 'PASS',
                    'details': f"Texto extraído: {len(extracted_text)} chars, Datos: {dni_data}"
                })
            else:
                raise Exception("OCR no devolvió texto válido")
                
        except Exception as e:
            logger.error(f"❌ Error en OCR: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': 'OCR Processing',
                'status': 'FAIL',
                'error': str(e)
            })
    
    def test_sheets_operations(self):
        """Probar operaciones de Google Sheets"""
        logger.info("🧪 Probando operaciones de Google Sheets...")
        self.test_results['total'] += 1
        
        try:
            from utils.sheets_manager import SheetsManager
            
            sheets = SheetsManager()
            
            # Probar obtener resumen diario
            logger.info("   Obteniendo resumen diario...")
            summary = sheets.get_daily_summary()
            
            if summary and 'total_clients' in summary:
                logger.info(f"✅ Resumen obtenido: {summary['total_clients']} clientes hoy")
                
                # Probar disponibilidad de habitaciones
                logger.info("   Obteniendo disponibilidad de habitaciones...")
                availability = sheets.get_room_availability()
                
                if availability and 'available' in availability:
                    logger.info(f"✅ Disponibilidad obtenida: {len(availability['available'])} habitaciones disponibles")
                    
                    self.test_results['passed'] += 1
                    self.test_results['details'].append({
                        'test': 'Google Sheets Operations',
                        'status': 'PASS',
                        'details': f"Clientes hoy: {summary['total_clients']}, Habitaciones disponibles: {len(availability['available'])}"
                    })
                else:
                    raise Exception("No se pudo obtener disponibilidad")
            else:
                raise Exception("No se pudo obtener resumen")
                
        except Exception as e:
            logger.error(f"❌ Error en Google Sheets: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': 'Google Sheets Operations', 
                'status': 'FAIL',
                'error': str(e)
            })
    
    def test_drive_operations(self):
        """Probar operaciones de Google Drive"""
        logger.info("🧪 Probando operaciones de Google Drive...")
        self.test_results['total'] += 1
        
        try:
            from utils.drive_manager import DriveManager
            
            drive = DriveManager()
            
            # Crear imagen de prueba para subir
            test_image = self.create_test_image()
            if not test_image:
                raise Exception("No se pudo crear imagen de prueba")
            
            # Probar subida de archivo
            logger.info("   Subiendo imagen de prueba...")
            result = drive.upload_dni_photo(
                test_image,
                "TEST12345678",
                "PRUEBA FUNCIONAL"
            )
            
            if result and 'file_id' in result:
                logger.info(f"✅ Imagen subida exitosamente: {result['filename']}")
                
                # Probar listado de archivos
                logger.info("   Listando archivos...")
                files = drive.list_dni_photos(limit=10)
                
                if files and len(files) > 0:
                    logger.info(f"✅ {len(files)} archivos encontrados")
                    
                    # Limpiar: eliminar archivo de prueba
                    try:
                        drive.delete_dni_photo(result['file_id'])
                        logger.info("✅ Archivo de prueba eliminado")
                    except:
                        logger.warning("⚠️  No se pudo eliminar archivo de prueba")
                    
                    self.test_results['passed'] += 1
                    self.test_results['details'].append({
                        'test': 'Google Drive Operations',
                        'status': 'PASS', 
                        'details': f"Subida exitosa: {result['filename']}, {len(files)} archivos totales"
                    })
                else:
                    raise Exception("No se pudieron listar archivos")
            else:
                raise Exception("Error en subida de archivo")
                
        except Exception as e:
            logger.error(f"❌ Error en Google Drive: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': 'Google Drive Operations',
                'status': 'FAIL',
                'error': str(e)
            })
    
    def test_bot_commands_simulation(self):
        """Simular comandos del bot (sin Telegram real)"""
        logger.info("🧪 Simulando comandos del bot...")
        
        # Test comando /start
        self.test_results['total'] += 1
        try:
            # Simular usuario autorizado
            test_user_id = int(os.getenv('AUTHORIZED_USERS', '123456789').split(',')[0])
            
            # Crear mock objects para simular Telegram
            class MockUser:
                def __init__(self, user_id):
                    self.id = user_id
                    self.first_name = "Test User"
            
            class MockMessage:
                def __init__(self, user_id):
                    self.effective_user = MockUser(user_id)
                
                def reply_text(self, text, **kwargs):
                    logger.info(f"   Bot respondería: {text[:100]}...")
                    return True
            
            class MockContext:
                pass
            
            # Probar comando /start
            mock_update = MockMessage(test_user_id)
            mock_context = MockContext()
            
            # Probar si el usuario está autorizado
            is_authorized = self.bot.is_authorized(test_user_id)
            
            if is_authorized:
                logger.info("✅ Usuario autorizado verificado")
                # Simular llamada al comando start
                try:
                    self.bot.start(mock_update, mock_context)
                    logger.info("✅ Comando /start simulado exitosamente")
                    
                    self.test_results['passed'] += 1
                    self.test_results['details'].append({
                        'test': 'Bot Commands Simulation',
                        'status': 'PASS',
                        'details': f"Usuario {test_user_id} autorizado, comando /start funcional"
                    })
                except Exception as e:
                    raise Exception(f"Error en comando /start: {e}")
            else:
                raise Exception("Usuario de prueba no autorizado")
                
        except Exception as e:
            logger.error(f"❌ Error en simulación de comandos: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': 'Bot Commands Simulation',
                'status': 'FAIL',
                'error': str(e)
            })
    
    def test_complete_registration_flow(self):
        """Probar flujo completo de registro (simulado)"""
        logger.info("🧪 Probando flujo completo de registro...")
        self.test_results['total'] += 1
        
        try:
            # Datos de cliente de prueba
            test_client_data = {
                'fecha': datetime.now().strftime('%Y-%m-%d'),
                'hora_ingreso': datetime.now().strftime('%H:%M'),
                'hora_salida_estimada': '17:00',
                'habitacion': '999',  # Habitación de prueba
                'dni': 'TEST12345678',
                'nombre': 'CLIENTE DE PRUEBA FUNCIONAL',
                'nacionalidad': 'PERUANA',
                'duracion': '3 horas',
                'precio': 'S/30',
                'forma_pago': 'Efectivo',
                'observaciones': 'Registro de prueba funcional - ELIMINAR',
                'registrado_por': 'Test System'
            }
            
            logger.info("   Simulando guardado completo...")
            
            # Probar guardado en Sheets
            from utils.sheets_manager import SheetsManager
            sheets = SheetsManager()
            
            logger.info("   Guardando en Google Sheets...")
            sheets_result = sheets.save_client_data(test_client_data)
            
            if not sheets_result:
                raise Exception("Error al guardar en Google Sheets")
            
            logger.info("✅ Datos guardados en Google Sheets")
            
            # Probar subida de foto (simulada)
            from utils.drive_manager import DriveManager
            drive = DriveManager()
            
            test_image = self.create_test_image()
            if test_image:
                logger.info("   Subiendo foto de DNI...")
                drive_result = drive.upload_dni_photo(
                    test_image,
                    test_client_data['dni'],
                    test_client_data['nombre']
                )
                
                if drive_result:
                    logger.info("✅ Foto subida a Google Drive")
                    
                    # Limpiar archivo de prueba
                    try:
                        drive.delete_dni_photo(drive_result['file_id'])
                        logger.info("✅ Archivo de prueba eliminado")
                    except:
                        logger.warning("⚠️  No se pudo eliminar archivo de prueba")
                else:
                    raise Exception("Error al subir foto a Google Drive")
            
            logger.info("✅ Flujo completo de registro simulado exitosamente")
            
            self.test_results['passed'] += 1
            self.test_results['details'].append({
                'test': 'Complete Registration Flow',
                'status': 'PASS',
                'details': f"Cliente {test_client_data['dni']} registrado completamente"
            })
            
        except Exception as e:
            logger.error(f"❌ Error en flujo completo: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': 'Complete Registration Flow',
                'status': 'FAIL', 
                'error': str(e)
            })
    
    def test_error_handling(self):
        """Probar manejo de errores"""
        logger.info("🧪 Probando manejo de errores...")
        self.test_results['total'] += 1
        
        try:
            # Probar con usuario no autorizado
            unauthorized_user = 999999999  # ID que no está en AUTHORIZED_USERS
            
            is_unauthorized = not self.bot.is_authorized(unauthorized_user)
            
            if is_unauthorized:
                logger.info("✅ Usuario no autorizado correctamente rechazado")
            else:
                raise Exception("Usuario no autorizado fue aceptado")
            
            # Probar OCR con imagen inválida
            from utils.ocr_processor import OCRProcessor
            ocr = OCRProcessor()
            
            # Imagen muy pequeña (debería fallar graciosamente)
            tiny_image = Image.new('RGB', (10, 10), color='white')
            img_bytes = BytesIO()
            tiny_image.save(img_bytes, format='JPEG')
            tiny_bytes = img_bytes.getvalue()
            
            logger.info("   Probando OCR con imagen inválida...")
            result = ocr.extract_text_from_image(tiny_bytes)
            
            # Debería devolver string vacío o manejar el error graciosamente
            if result is not None:  # Manejo gracioso del error
                logger.info("✅ OCR maneja errores graciosamente")
            else:
                raise Exception("OCR no maneja errores correctamente")
            
            self.test_results['passed'] += 1
            self.test_results['details'].append({
                'test': 'Error Handling',
                'status': 'PASS',
                'details': "Usuario no autorizado rechazado, OCR maneja errores graciosamente"
            })
            
        except Exception as e:
            logger.error(f"❌ Error en manejo de errores: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': 'Error Handling',
                'status': 'FAIL',
                'error': str(e)
            })
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas funcionales"""
        logger.info("🚀 INICIANDO PRUEBAS FUNCIONALES COMPLETAS - HOTELBOT")
        logger.info("="*70)
        
        start_time = time.time()
        
        # Configurar bot
        if not self.setup_bot():
            logger.error("❌ No se pudo inicializar el bot - abortando pruebas")
            return False
        
        # Lista de pruebas funcionales
        tests = [
            ("OCR Processing", self.test_ocr_processing),
            ("Google Sheets Operations", self.test_sheets_operations), 
            ("Google Drive Operations", self.test_drive_operations),
            ("Bot Commands Simulation", self.test_bot_commands_simulation),
            ("Complete Registration Flow", self.test_complete_registration_flow),
            ("Error Handling", self.test_error_handling),
        ]
        
        # Ejecutar cada prueba
        for test_name, test_func in tests:
            logger.info(f"\n{'-'*50}")
            logger.info(f"🧪 Ejecutando: {test_name}")
            
            try:
                test_func()
                time.sleep(1)  # Pausa entre pruebas
            except Exception as e:
                logger.error(f"❌ Error crítico en {test_name}: {e}")
                self.test_results['total'] += 1
                self.test_results['failed'] += 1
                self.test_results['details'].append({
                    'test': test_name,
                    'status': 'FAIL',
                    'error': f"Error crítico: {e}"
                })
        
        # Generar reporte final
        self.generate_final_report(time.time() - start_time)
        
        return self.test_results['failed'] == 0
    
    def generate_final_report(self, elapsed_time):
        """Generar reporte final de pruebas funcionales"""
        logger.info("\n" + "="*70)
        logger.info("📊 REPORTE FINAL - PRUEBAS FUNCIONALES")
        logger.info("="*70)
        
        success_rate = (self.test_results['passed'] / self.test_results['total'] * 100) if self.test_results['total'] > 0 else 0
        
        # Mostrar resumen por prueba
        for detail in self.test_results['details']:
            status_icon = "✅" if detail['status'] == 'PASS' else "❌"
            logger.info(f"{status_icon} {detail['test']}")
            
            if detail['status'] == 'PASS' and 'details' in detail:
                logger.info(f"   📋 {detail['details']}")
            elif detail['status'] == 'FAIL' and 'error' in detail:
                logger.error(f"   ❌ {detail['error']}")
        
        logger.info("-"*70)
        logger.info(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
        logger.info(f"🧪 Total de pruebas: {self.test_results['total']}")
        logger.info(f"✅ Exitosas: {self.test_results['passed']}")
        logger.info(f"❌ Fallidas: {self.test_results['failed']}")
        logger.info(f"📊 Tasa de éxito: {success_rate:.1f}%")
        
        if self.test_results['failed'] == 0:
            logger.info("\n🎉 ¡TODAS LAS PRUEBAS FUNCIONALES PASARON!")
            logger.info("🚀 Tu HotelBot está 100% funcional y listo para producción")
            logger.info("📱 Puedes usar el bot en Telegram con confianza")
        else:
            logger.warning(f"\n⚠️  {self.test_results['failed']} pruebas funcionales fallaron")
            logger.info("🔧 Revisa los errores arriba para diagnosticar problemas")
        
        logger.info("="*70)
        
        # Guardar reporte
        report = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_time': elapsed_time,
            'success_rate': success_rate,
            'summary': {
                'total': self.test_results['total'],
                'passed': self.test_results['passed'], 
                'failed': self.test_results['failed']
            },
            'details': self.test_results['details']
        }
        
        report_file = f"functional_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Reporte guardado en: {report_file}")

def main():
    """Función principal"""
    try:
        tester = BotFunctionalTester()
        success = tester.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Pruebas interrumpidas por el usuario")
        return 1
    except Exception as e:
        logger.error(f"\n💥 Error crítico en las pruebas: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 