import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración del bot de hotel"""
    
    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    
    # Usuarios autorizados
    AUTHORIZED_USERS = [
        int(user_id) for user_id in os.getenv('AUTHORIZED_USERS', '').split(',') 
        if user_id.strip()
    ]
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google Cloud Service Account (para Sheets)
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Google OAuth Credentials (para Drive)
    GOOGLE_OAUTH_CREDENTIALS = os.getenv('GOOGLE_OAUTH_CREDENTIALS', 'credentials/credentials.json')
    
    # Google Sheets
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    GOOGLE_SHEETS_WORKSHEET_NAME = os.getenv('GOOGLE_SHEETS_WORKSHEET_NAME', 'Registros')
    
    # Google Drive
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    # Configuración general
    TIMEZONE = os.getenv('TIMEZONE', 'America/Lima')
    
    # Opciones del formulario
    DURACION_OPCIONES = ['2 horas', '3 horas', 'noche']
    PRECIO_OPCIONES = ['S/25', 'S/30', 'S/40']
    PAGO_OPCIONES = ['Efectivo', 'Yape', 'Plin', 'Transferencia']
    HABITACIONES = [str(i) for i in range(1, 11)]  # Del 1 al 10
    
    @classmethod
    def validate_config(cls):
        """Valida que todas las configuraciones necesarias estén presentes"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'OPENAI_API_KEY',
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_SHEETS_SPREADSHEET_ID',
            'GOOGLE_DRIVE_FOLDER_ID'
        ]
        
        # GOOGLE_OAUTH_CREDENTIALS es opcional, usa default si no está definida
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
        
        return True 