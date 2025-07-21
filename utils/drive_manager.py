from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
import io
import logging
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

class DriveManager:
    """Manejador para Google Drive usando OAuth authentication"""
    
    # Google Drive API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.service = None
        self.credentials_file = Path(Config.GOOGLE_OAUTH_CREDENTIALS)
        self.token_file = Path("credentials/token.json")  # Token para OAuth
        self._authenticate()
    
    def _authenticate(self):
        """Autenticación con Google Drive usando OAuth"""
        try:
            creds = None
            
            # Load existing token
            if self.token_file.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(self.token_file), self.SCOPES)
                except Exception as e:
                    logger.warning(f"No se pudo cargar token existente: {e}")
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        logger.info("Token de Google Drive renovado exitosamente")
                    except Exception as e:
                        logger.warning(f"No se pudo renovar token: {e}")
                        creds = None
                
                if not creds:
                    if not self.credentials_file.exists():
                        logger.error(f"Archivo de credenciales no encontrado: {self.credentials_file}")
                        raise FileNotFoundError("Archivo credentials.json no encontrado")
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(self.credentials_file), self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        logger.info("Autenticación OAuth completada exitosamente")
                    except Exception as e:
                        logger.error(f"Fallo en autenticación OAuth: {e}")
                        raise
                
                # Save the credentials for next run
                try:
                    # Crear directorio credentials si no existe
                    self.token_file.parent.mkdir(exist_ok=True)
                    
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                    logger.info(f"Token guardado in: {self.token_file}")
                except Exception as e:
                    logger.warning(f"No se pudo guardar token: {e}")
            
            # Crear servicio de Google Drive
            self.service = build('drive', 'v3', credentials=creds)
            
            logger.info("Autenticación con Google Drive exitosa")
            
        except Exception as e:
            logger.error(f"Error al autenticar con Google Drive: {str(e)}")
            raise
    
    def upload_dni_photo(self, image_bytes, dni, client_name=None):
        """Subir foto de DNI a Google Drive"""
        try:
            # Crear nombre único para el archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"DNI_{dni}_{timestamp}.jpg"
            
            if client_name:
                # Limpiar nombre del cliente para usar en el archivo
                clean_name = ''.join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"DNI_{dni}_{clean_name}_{timestamp}.jpg"
            
            # Crear objeto de archivo
            media = MediaIoBaseUpload(
                io.BytesIO(image_bytes),
                mimetype='image/jpeg',
                resumable=True
            )
            
            # Metadatos del archivo
            file_metadata = {
                'name': filename,
                'parents': [Config.GOOGLE_DRIVE_FOLDER_ID]
            }
            
            # Subir archivo
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink'
            ).execute()
            
            # Hacer el archivo público (opcional)
            self._make_file_public(file['id'])
            
            logger.info(f"Foto de DNI subida exitosamente: {filename}")
            
            return {
                'file_id': file['id'],
                'filename': filename,
                'web_view_link': file['webViewLink'],
                'web_content_link': file['webContentLink']
            }
            
        except Exception as e:
            logger.error(f"Error al subir foto de DNI: {str(e)}")
            return None
    
    def _make_file_public(self, file_id):
        """Hacer el archivo público para que sea accesible"""
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
        except Exception as e:
            logger.warning(f"No se pudo hacer público el archivo: {str(e)}")
    
    def get_folder_info(self):
        """Obtener información de la carpeta de almacenamiento"""
        try:
            folder = self.service.files().get(
                fileId=Config.GOOGLE_DRIVE_FOLDER_ID,
                fields='name,id,webViewLink'
            ).execute()
            
            return folder
            
        except Exception as e:
            logger.error(f"Error al obtener información de la carpeta: {str(e)}")
            return None
    
    def list_dni_photos(self, limit=50):
        """Listar fotos de DNI almacenadas"""
        try:
            # Buscar archivos en la carpeta
            query = f"'{Config.GOOGLE_DRIVE_FOLDER_ID}' in parents and mimeType contains 'image/'"
            
            results = self.service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id,name,createdTime,webViewLink,size)"
            ).execute()
            
            files = results.get('files', [])
            
            return files
            
        except Exception as e:
            logger.error(f"Error al listar fotos de DNI: {str(e)}")
            return []
    
    def delete_dni_photo(self, file_id):
        """Eliminar foto de DNI"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Foto de DNI eliminada: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar foto de DNI: {str(e)}")
            return False
    
    def get_storage_usage(self):
        """Obtener información de uso de almacenamiento"""
        try:
            # Obtener información de la cuenta
            about = self.service.about().get(fields='storageQuota').execute()
            
            storage_quota = about.get('storageQuota', {})
            
            return {
                'limit': int(storage_quota.get('limit', 0)),
                'usage': int(storage_quota.get('usage', 0)),
                'usage_in_drive': int(storage_quota.get('usageInDrive', 0))
            }
            
        except Exception as e:
            logger.error(f"Error al obtener información de almacenamiento: {str(e)}")
            return {
                'limit': 0,
                'usage': 0,
                'usage_in_drive': 0
            }
    
    def create_backup_folder(self, folder_name):
        """Crear carpeta de respaldo"""
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [Config.GOOGLE_DRIVE_FOLDER_ID]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id,name'
            ).execute()
            
            logger.info(f"Carpeta de respaldo creada: {folder_name}")
            return folder['id']
            
        except Exception as e:
            logger.error(f"Error al crear carpeta de respaldo: {str(e)}")
            return None
    
    def move_file_to_folder(self, file_id, destination_folder_id):
        """Mover archivo a otra carpeta"""
        try:
            # Obtener información actual del archivo
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ','.join(file.get('parents', []))
            
            # Mover archivo
            self.service.files().update(
                fileId=file_id,
                addParents=destination_folder_id,
                removeParents=previous_parents,
                fields='id,parents'
            ).execute()
            
            logger.info(f"Archivo movido a nueva carpeta: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al mover archivo: {str(e)}")
            return False 