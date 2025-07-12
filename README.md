# 🏨 Bot de Registro de Clientes para Hotel

Bot de Telegram para registro de clientes de hotel con OCR, integración con Google Sheets y Google Drive.

## 🚀 Características

- **OCR automático**: Extracción de datos de DNI usando Google Cloud Vision API
- **Formulario conversacional**: Guía paso a paso para registrar clientes
- **Google Sheets**: Almacenamiento automático de registros
- **Google Drive**: Backup seguro de fotos de DNI
- **Seguridad**: Acceso restringido solo a personal autorizado
- **Informes**: Resumen diario y disponibilidad de habitaciones
- **Multiusuario**: Soporte para múltiples usuarios del hotel

## 📋 Requisitos

- Python 3.8+
- Cuenta de Google Cloud con APIs habilitadas
- Bot de Telegram creado con BotFather
- Google Sheets y Google Drive configurados

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd HotelBot
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Google Cloud

#### Habilitar APIs
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita las siguientes APIs:
   - Google Cloud Vision API
   - Google Sheets API
   - Google Drive API

#### Crear credenciales
1. Ve a **IAM & Admin** > **Service Accounts**
2. Crea una nueva cuenta de servicio
3. Descarga el archivo JSON de credenciales
4. Guarda el archivo en `credentials/hotel-bot-credentials.json`

### 4. Configurar Google Sheets

1. Crea una nueva hoja de cálculo en Google Sheets
2. Comparte la hoja con el email de la cuenta de servicio
3. Copia el ID de la hoja de cálculo desde la URL

### 5. Configurar Google Drive

1. Crea una carpeta en Google Drive para las fotos
2. Comparte la carpeta con el email de la cuenta de servicio
3. Copia el ID de la carpeta desde la URL

### 6. Configurar el Bot de Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un nuevo bot con `/newbot`
3. Guarda el token del bot

### 7. Configurar variables de entorno

1. Copia el archivo de ejemplo:
   ```bash
   cp config_example.env .env
   ```

2. Edita el archivo `.env` con tus datos:
   ```env
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   TELEGRAM_ADMIN_CHAT_ID=tu_chat_id
   AUTHORIZED_USERS=user1,user2,user3
   GOOGLE_APPLICATION_CREDENTIALS=credentials/hotel-bot-credentials.json
   GOOGLE_SHEETS_SPREADSHEET_ID=tu_spreadsheet_id
   GOOGLE_SHEETS_WORKSHEET_NAME=Registros
   GOOGLE_DRIVE_FOLDER_ID=tu_folder_id
   TIMEZONE=America/Lima
   ```

## 🔧 Configuración Detallada

### Obtener Chat ID

Para obtener tu Chat ID:
1. Envía un mensaje a tu bot
2. Ve a: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
3. Busca tu `chat_id` en la respuesta

### Configurar usuarios autorizados

En el archivo `.env`, agrega los Chat IDs de los usuarios autorizados:
```env
AUTHORIZED_USERS=123456789,987654321,555666777
```

### Estructura de Google Sheets

El bot creará automáticamente los siguientes encabezados:
- Fecha
- Hora Ingreso
- Hora Salida Estimada
- Habitación
- DNI
- Nombre
- Nacionalidad
- Duración
- Precio
- Forma de Pago
- Observaciones
- Registrado por

## 🚀 Uso

### Ejecutar el bot

```bash
python hotel_bot.py
```

### Comandos disponibles

- `/start` - Iniciar el bot
- `/nuevo` - Registrar nuevo cliente
- `/resumen` - Ver resumen del día
- `/habitaciones` - Ver disponibilidad de habitaciones
- `/ayuda` - Obtener ayuda

### Flujo de registro

1. **Enviar foto del DNI**: El usuario envía una foto del DNI del cliente
2. **OCR automático**: El bot extrae los datos automáticamente
3. **Verificar datos**: El usuario verifica y edita si es necesario
4. **Completar información**: El bot pregunta:
   - Duración de estancia
   - Precio cobrado
   - Forma de pago
   - Habitación
   - Observaciones
5. **Confirmar y guardar**: Los datos se guardan en Google Sheets y la foto en Google Drive

## 🧪 Guía de Pruebas

### Pasos para Probar el Bot

#### 1. **Configurar Google Cloud** 🌐

1. **Ir a Google Cloud Console**:
   - Visita: https://console.cloud.google.com/
   - Crea un nuevo proyecto o selecciona uno existente

2. **Habilitar APIs necesarias**:
   - Ve a "APIs & Services" > "Library"
   - Busca y habilita:
     - Google Cloud Vision API
     - Google Sheets API
     - Google Drive API

3. **Crear cuenta de servicio**:
   - Ve a "IAM & Admin" > "Service Accounts"
   - Clic en "Create Service Account"
   - Nombre: `hotel-bot-service`
   - Rol: `Editor`
   - Clic en "Create Key" > JSON
   - Descargar el archivo JSON

4. **Guardar credenciales**:
   - Renombrar el archivo descargado como `hotel-bot-credentials.json`
   - Copiarlo en la carpeta `credentials/`

#### 2. **Crear Bot en Telegram** 🤖

1. **Hablar con BotFather**:
   - Buscar `@BotFather` en Telegram
   - Enviar `/newbot`
   - Elegir nombre: `Hotel Registration Bot`
   - Elegir username: `tu_hotel_bot`

2. **Guardar token**:
   - Copiar el token que te da BotFather
   - Formato: `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg`

3. **Obtener tu Chat ID**:
   - Enviar un mensaje a tu bot
   - Visitar: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Copiar tu `chat_id` de la respuesta

#### 3. **Configurar Google Sheets** 📊

1. **Crear hoja de cálculo**:
   - Ir a Google Sheets
   - Crear nueva hoja: "Registros Hotel"
   - Copiar el ID de la URL (parte larga entre /d/ y /edit)

2. **Compartir con el bot**:
   - Clic en "Compartir"
   - Agregar el email de la cuenta de servicio (del archivo JSON)
   - Dar permisos de "Editor"

#### 4. **Configurar Google Drive** 📁

1. **Crear carpeta**:
   - Ir a Google Drive
   - Crear nueva carpeta: "Fotos DNI Hotel"
   - Copiar el ID de la URL (parte final después de /folders/)

2. **Compartir carpeta**:
   - Clic derecho > "Compartir"
   - Agregar el email de la cuenta de servicio
   - Dar permisos de "Editor"

#### 5. **Configurar Variables de Entorno** ⚙️

1. **Crear archivo .env**:
   ```bash
   cp config_example.env .env
   ```

2. **Editar archivo .env** con tus datos:
   ```env
   TELEGRAM_BOT_TOKEN=tu_token_del_bot
   TELEGRAM_ADMIN_CHAT_ID=tu_chat_id
   AUTHORIZED_USERS=tu_chat_id,otro_chat_id
   GOOGLE_APPLICATION_CREDENTIALS=credentials/hotel-bot-credentials.json
   GOOGLE_SHEETS_SPREADSHEET_ID=tu_spreadsheet_id
   GOOGLE_SHEETS_WORKSHEET_NAME=Registros
   GOOGLE_DRIVE_FOLDER_ID=tu_folder_id
   TIMEZONE=America/Lima
   ```

#### 6. **Instalar Dependencias** 📦

```bash
pip install -r requirements.txt
```

#### 7. **Probar el Bot** 🚀

1. **Ejecutar con verificación**:
   ```bash
   python start_bot.py
   ```

2. **Si todo está bien configurado, verás**:
   ```
   🏨 Bot de Registro de Clientes - Hotel
   ==================================================
   
   🔍 Verificando configuración...
   ✅ Todas las dependencias están instaladas
   ✅ Variables de entorno configuradas
   ✅ Archivo de credenciales encontrado
   ✅ 1 usuario(s) autorizado(s)
   ✅ Configuración verificada exitosamente
   🚀 Iniciando bot...
   ```

#### 8. **Pruebas en Telegram** 📱

1. **Iniciar conversación**:
   - Buscar tu bot en Telegram
   - Enviar `/start`
   - Deberías ver el mensaje de bienvenida

2. **Probar comandos**:
   - `/nuevo` - Iniciar registro
   - `/resumen` - Ver resumen del día
   - `/habitaciones` - Ver disponibilidad
   - `/ayuda` - Ver ayuda

3. **Probar flujo completo**:
   - Enviar `/nuevo`
   - Enviar una foto de DNI (puedes usar una imagen de prueba)
   - Completar el formulario paso a paso
   - Confirmar el registro

#### 9. **Verificar Resultados** ✅

1. **En Google Sheets**:
   - Revisar que se creó una fila con los datos
   - Verificar que todos los campos estén llenos

2. **En Google Drive**:
   - Revisar que se subió la foto del DNI
   - Verificar que el nombre incluya timestamp

3. **En Telegram**:
   - Probar `/resumen` para ver el registro
   - Probar `/habitaciones` para ver disponibilidad

#### 10. **Solución de Problemas** 🔧

**Si el bot no responde**:
- Verificar que el token sea correcto
- Revisar que tu chat_id esté en AUTHORIZED_USERS

**Si hay error de OCR**:
- Verificar que Google Cloud Vision API esté habilitada
- Revisar que las credenciales sean correctas

**Si no guarda en Sheets**:
- Verificar que la hoja esté compartida con la cuenta de servicio
- Revisar que el ID de la hoja sea correcto

**Si no guarda en Drive**:
- Verificar que la carpeta esté compartida
- Revisar que el ID de la carpeta sea correcto

### Ejemplo de Foto de DNI para Pruebas 📸

Puedes usar cualquier imagen clara de un DNI para probar. El bot intentará extraer:
- Nombre
- Número de DNI
- Fecha de nacimiento
- Nacionalidad

### Resultado Esperado 🎯

Después de un registro exitoso, verás:
- Una fila nueva en Google Sheets con todos los datos
- Una foto guardada en Google Drive
- Un mensaje de confirmación en Telegram

## 📊 Funcionalidades

### OCR de DNI

El bot puede extraer:
- Nombre completo
- Número de DNI
- Fecha de nacimiento
- Nacionalidad (Peruana, Venezolana, Colombiana, Ecuatoriana)

### Gestión de habitaciones

- Visualización de disponibilidad en tiempo real
- Habitaciones del 1 al 10 (configurable)
- Opción de habitación personalizada

### Reportes

- Resumen diario con total de clientes e ingresos
- Historial de registros
- Disponibilidad de habitaciones

## 🔒 Seguridad

- **Acceso restringido**: Solo usuarios autorizados pueden usar el bot
- **Backup seguro**: Fotos almacenadas en Google Drive
- **Logs**: Registro de actividades para auditoria

## 📱 Deployment

### Heroku

1. Crea una app en Heroku
2. Configura las variables de entorno
3. Sube el archivo de credenciales
4. Deploy con Git

### Railway

1. Conecta tu repositorio
2. Configura las variables de entorno
3. Deploy automático

### VPS

1. Instala Python y dependencias
2. Configura el archivo `.env`
3. Ejecuta con `python hotel_bot.py`
4. Usa systemd para mantener el bot ejecutándose

## 📝 Logs

El bot genera logs detallados en:
- Consola durante desarrollo
- Archivos de log en producción

## 🔧 Personalización

### Modificar opciones

En `config.py` puedes cambiar:
- Opciones de duración
- Precios predefinidos
- Formas de pago
- Número de habitaciones

### Agregar funcionalidades

El bot está diseñado para ser extensible. Puedes agregar:
- Nuevos comandos
- Integración con otras APIs
- Notificaciones automáticas
- Reportes avanzados

## 🐛 Solución de problemas

### Bot no responde
- Verifica el token del bot
- Revisa que el bot esté agregado a los chats

### Error de OCR
- Verifica las credenciales de Google Cloud
- Asegúrate de que la API esté habilitada

### Error de Google Sheets
- Verifica permisos de la hoja
- Revisa el ID de la hoja de cálculo

### Error de Google Drive
- Verifica permisos de la carpeta
- Revisa el ID de la carpeta

## 📞 Soporte

Para soporte técnico:
1. Revisa los logs del bot
2. Verifica la configuración
3. Consulta la documentación de APIs

## 🏗️ Arquitectura

```
HotelBot/
├── hotel_bot.py           # Bot principal
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── config_example.env     # Ejemplo de configuración
├── utils/
│   ├── __init__.py
│   ├── ocr_processor.py   # Procesamiento OCR
│   ├── sheets_manager.py  # Gestión Google Sheets
│   └── drive_manager.py   # Gestión Google Drive
└── credentials/
    └── hotel-bot-credentials.json  # Credenciales Google
```

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📈 Roadmap

- [ ] Interfaz web para administración
- [ ] Integración con WhatsApp
- [ ] Notificaciones automáticas
- [ ] Reportes avanzados
- [ ] App móvil
- [ ] Integración con POS

---

Desarrollado con ❤️ para hoteles modernos 