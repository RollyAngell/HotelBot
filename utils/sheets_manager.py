import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from config import Config

logger = logging.getLogger(__name__)

class SheetsManager:
    """Manejador para Google Sheets"""
    
    def __init__(self):
        self.gc = None
        self.worksheet = None
        self._authenticate()
    
    def _authenticate(self):
        """Autenticación con Google Sheets"""
        try:
            # Definir el alcance
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file"
            ]
            
            # Autenticar usando el archivo de credenciales
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_APPLICATION_CREDENTIALS, 
                scopes=scope
            )
            
            # Crear cliente de gspread
            self.gc = gspread.authorize(creds)
            
            # Abrir la hoja de cálculo
            spreadsheet = self.gc.open_by_key(Config.GOOGLE_SHEETS_SPREADSHEET_ID)
            
            # Obtener o crear la hoja de trabajo
            try:
                self.worksheet = spreadsheet.worksheet(Config.GOOGLE_SHEETS_WORKSHEET_NAME)
            except gspread.WorksheetNotFound:
                # Crear nueva hoja si no existe
                self.worksheet = spreadsheet.add_worksheet(
                    title=Config.GOOGLE_SHEETS_WORKSHEET_NAME,
                    rows=1000,
                    cols=12
                )
                self._create_headers()
            
            logger.info("Autenticación con Google Sheets exitosa")
            
        except Exception as e:
            logger.error(f"Error al autenticar con Google Sheets: {str(e)}")
            raise
    
    def _create_headers(self):
        """Crear encabezados en la hoja de cálculo"""
        headers = [
            'Fecha',
            'Hora Ingreso',
            'Hora Salida Estimada',
            'Habitación',
            'DNI',
            'Nombre',
            'Nacionalidad',
            'Duración',
            'Precio',
            'Forma de Pago',
            'Observaciones',
            'Registrado por'
        ]
        
        try:
            self.worksheet.update('A1:L1', [headers])
            logger.info("Encabezados creados en Google Sheets")
        except Exception as e:
            logger.error(f"Error al crear encabezados: {str(e)}")
    
    def save_client_data(self, client_data):
        """Guardar datos del cliente en Google Sheets"""
        try:
            # Preparar los datos para insertar
            row_data = [
                client_data.get('fecha', ''),
                client_data.get('hora_ingreso', ''),
                client_data.get('hora_salida_estimada', ''),
                client_data.get('habitacion', ''),
                client_data.get('dni', ''),
                client_data.get('nombre', ''),
                client_data.get('nacionalidad', ''),
                client_data.get('duracion', ''),
                client_data.get('precio', ''),
                client_data.get('forma_pago', ''),
                client_data.get('observaciones', ''),
                client_data.get('registrado_por', '')
            ]
            
            # Insertar fila al final
            self.worksheet.append_row(row_data)
            
            logger.info(f"Datos del cliente guardados: DNI {client_data.get('dni', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar datos en Google Sheets: {str(e)}")
            return False
    
    def get_client_history(self, dni):
        """Obtener historial de un cliente por DNI"""
        try:
            # Buscar registros del cliente
            records = self.worksheet.get_all_records()
            client_records = [record for record in records if record.get('DNI') == dni]
            
            return client_records
            
        except Exception as e:
            logger.error(f"Error al obtener historial del cliente: {str(e)}")
            return []
    
    def get_room_availability(self):
        """Obtener disponibilidad de habitaciones"""
        try:
            # Obtener registros de hoy
            today = datetime.now().strftime('%Y-%m-%d')
            records = self.worksheet.get_all_records()
            
            # Filtrar registros de hoy
            today_records = [
                record for record in records 
                if record.get('Fecha') == today
            ]
            
            # Obtener habitaciones ocupadas
            occupied_rooms = [
                record.get('Habitación') for record in today_records
                if record.get('Habitación')
            ]
            
            # Calcular habitaciones disponibles
            all_rooms = set(Config.HABITACIONES)
            available_rooms = all_rooms - set(occupied_rooms)
            
            return {
                'available': list(available_rooms),
                'occupied': occupied_rooms
            }
            
        except Exception as e:
            logger.error(f"Error al obtener disponibilidad de habitaciones: {str(e)}")
            return {
                'available': Config.HABITACIONES,
                'occupied': []
            }
    
    def get_daily_summary(self, date=None):
        """Obtener resumen diario"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            records = self.worksheet.get_all_records()
            daily_records = [
                record for record in records 
                if record.get('Fecha') == date
            ]
            
            # Calcular estadísticas
            total_clients = len(daily_records)
            total_revenue = 0
            
            for record in daily_records:
                precio_str = record.get('Precio', '0')
                # Extraer número del precio (ej: S/30 -> 30)
                precio_num = ''.join(filter(str.isdigit, precio_str))
                if precio_num:
                    total_revenue += int(precio_num)
            
            return {
                'date': date,
                'total_clients': total_clients,
                'total_revenue': total_revenue,
                'records': daily_records
            }
            
        except Exception as e:
            logger.error(f"Error al obtener resumen diario: {str(e)}")
            return {
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'total_clients': 0,
                'total_revenue': 0,
                'records': []
            }
    
    def update_client_checkout(self, dni, checkout_time):
        """Actualizar hora de salida de un cliente"""
        try:
            # Buscar la fila del cliente
            records = self.worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Empezar desde fila 2
                if record.get('DNI') == dni and not record.get('Hora Salida Real'):
                    # Actualizar hora de salida real
                    col_index = len(record) + 1  # Nueva columna
                    self.worksheet.update_cell(i, col_index, checkout_time)
                    logger.info(f"Hora de salida actualizada para DNI {dni}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error al actualizar hora de salida: {str(e)}")
            return False 