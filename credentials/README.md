# Credenciales de Google Cloud

Este directorio debe contener el archivo de credenciales de Google Cloud:

## Configuración requerida

1. **Archivo de credenciales**: `hotel-bot-credentials.json`
   - Descárgalo desde Google Cloud Console
   - Configuración > IAM & Admin > Service Accounts
   - Crear cuenta de servicio con los siguientes permisos:
     - Google Cloud Vision API
     - Google Sheets API
     - Google Drive API

## Permisos necesarios

La cuenta de servicio debe tener:
- **Vision API User**: Para procesamiento OCR
- **Editor**: Para Google Sheets y Google Drive

## Configuración de Google Sheets

1. Comparte tu hoja de cálculo con el email de la cuenta de servicio
2. Otorga permisos de **Editor**

## Configuración de Google Drive

1. Comparte tu carpeta de Google Drive con el email de la cuenta de servicio
2. Otorga permisos de **Editor**

## Estructura del archivo JSON

Tu archivo de credenciales debe tener esta estructura:

```json
{
  "type": "service_account",
  "project_id": "tu-proyecto",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "tu-servicio@tu-proyecto.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## Seguridad

⚠️ **IMPORTANTE**: Nunca compartas este archivo en repositorios públicos.
El archivo `.gitignore` ya está configurado para excluir los archivos `.json` de este directorio. 