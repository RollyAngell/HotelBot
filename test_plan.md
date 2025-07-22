# 🧪 PLAN DE PRUEBAS COMPLETO - HotelBot

## **PREPARACIÓN PREVIA** 📋

### **A. Obtener Credenciales de OpenAI** 🤖
1. **Ir a**: https://platform.openai.com/
2. **Crear cuenta** o iniciar sesión
3. **Ir a**: API Keys → Create new secret key
4. **Copiar la clave**: `sk-proj-...` (guarda en lugar seguro)
5. **Verificar créditos**: Asegúrate de tener saldo disponible

### **B. Configurar Google Cloud** ☁️
1. **Google Cloud Console**: https://console.cloud.google.com/
2. **Crear proyecto nuevo** o usar existente
3. **Habilitar APIs**:
   - Google Cloud Vision API ✅
   - Google Sheets API ✅
   - Google Drive API ✅
4. **Crear Service Account**:
   - IAM & Admin → Service Accounts
   - Create Service Account: "hotel-bot-service"
   - Role: "Editor"
   - Create Key → JSON
   - Descargar como: `hotel-bot-service-account.json`

### **C. Configurar Google Sheets** 📊
1. **Crear nueva hoja**: "Registros Hotel Bot"
2. **Copiar ID** de la URL: `1A2B3C4D5E...`
3. **Compartir con Service Account**:
   - Clic en "Compartir"
   - Agregar email del service account (del archivo JSON)
   - Rol: "Editor"

### **D. Configurar Google Drive** 📁
1. **Crear carpeta**: "Fotos DNI Hotel"
2. **Copiar ID** de la URL: después de `/folders/`
3. **Configurar OAuth**:
   - Google Cloud Console → APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: "Desktop application"
   - Descargar como: `credentials.json`

### **E. Crear Bot de Telegram** 🤖
1. **Buscar** `@BotFather` en Telegram
2. **Comando**: `/newbot`
3. **Nombre**: "Hotel Registration Bot"
4. **Username**: `tu_hotel_registration_bot`
5. **Guardar token**: `123456:ABC-DEF...`

### **F. Obtener tu Chat ID** 👤
1. **Enviar mensaje** a tu bot
2. **Visitar**: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. **Copiar** tu `chat_id`: número positivo o negativo

---

## **FASE 1: CONFIGURACIÓN Y VALIDACIÓN** ⚙️

### **1.1 Configurar Variables de Entorno** 📝

```bash
# Copiar archivo de ejemplo
cp config_example.env .env

# Editar archivo .env con tus datos
```

```env
# Tu archivo .env debe contener:
TELEGRAM_BOT_TOKEN=tu_token_del_bot
TELEGRAM_ADMIN_CHAT_ID=tu_chat_id
AUTHORIZED_USERS=tu_chat_id,otro_usuario_opcional
OPENAI_API_KEY=sk-proj-tu_clave_openai
GOOGLE_APPLICATION_CREDENTIALS=credentials/hotel-bot-service-account.json
GOOGLE_OAUTH_CREDENTIALS=credentials/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=tu_id_de_spreadsheet
GOOGLE_SHEETS_WORKSHEET_NAME=Registros
GOOGLE_DRIVE_FOLDER_ID=tu_id_de_carpeta_drive
TIMEZONE=America/Lima
```

### **1.2 Instalar Dependencias** 📦

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import telegram, openai, gspread, PIL; print('✅ Todas las dependencias instaladas')"
```

### **1.3 Validar Configuración** ✅

```bash
# Ejecutar script de validación
python start_bot.py
```

**Resultado esperado**:
```
🏨 Bot de Registro de Clientes - Hotel
==================================================

🔍 Verificando configuración...

📦 Verificando dependencias...
✅ Todas las dependencias están instaladas

🔧 Verificando variables de entorno...
✅ Archivo .env cargado
✅ Variables de entorno configuradas

🔐 Verificando credenciales...
✅ Archivo de credenciales encontrado

👥 Verificando usuarios autorizados...
✅ 1 usuario(s) autorizado(s)

✅ Configuración verificada exitosamente
🚀 Iniciando bot...
```

---

## **FASE 2: PRUEBAS DE FUNCIONALIDAD** 🧪

### **2.1 PRUEBA: Comando /start** 🚀

**Objetivo**: Verificar autenticación y mensaje de bienvenida

**Pasos**:
1. Buscar tu bot en Telegram
2. Enviar: `/start`

**Resultado esperado**:
```
🏨 Bot de Registro de Clientes

¡Hola! Soy el bot del hotel para registrar clientes.

✨ Nuevas mejoras:
• Procesamiento avanzado de imágenes de DNI
• Funciona con fotos desde cualquier ángulo
• Reconocimiento mejorado de texto

Comandos disponibles:
• /nuevo - Registrar nuevo cliente
• /resumen - Ver resumen del día
• /habitaciones - Ver disponibilidad
• /ayuda - Obtener ayuda

Para comenzar, envía una foto del DNI del cliente o usa /nuevo
```

**✅ Verificar**: Mensaje completo recibido correctamente

---

### **2.2 PRUEBA: Comando /nuevo** 📝

**Objetivo**: Iniciar proceso de registro

**Pasos**:
1. Enviar: `/nuevo`

**Resultado esperado**:
```
📷 Nuevo Cliente

Por favor, envía una foto del DNI del cliente para comenzar el registro.

```

**✅ Verificar**: Bot espera foto del DNI

---

### **2.3 PRUEBA: Procesamiento OCR** 📸

**Objetivo**: Probar extracción de datos del DNI

**Pasos**:
1. **Preparar imagen de DNI** (puede ser tuya o de ejemplo)
2. **Enviar foto** al bot
3. **Esperar procesamiento** (5-15 segundos)

**Resultado esperado**:
```
⏳ Procesando imagen del DNI...

🔍 Analizando imagen con IA avanzada
🖼️ Mejorando calidad automáticamente
📝 Extrayendo datos del documento

Esto puede tomar unos segundos.
```

**Luego**:
```
✅ ¡Excelente! Datos extraídos correctamente

📋 Datos extraídos del DNI:

👤 Nombre: PÉREZ GARCÍA JUAN CARLOS
🆔 DNI: 12345678
📅 Fecha Nacimiento: 15/03/1985
🌍 Nacionalidad: PERUANA

[Botones: ✅ Continuar | ✏️ Editar datos | 🔄 Reiniciar | ❌ Cancelar]
```

**✅ Verificar**: 
- Datos extraídos correctamente
- Nombres completos reconocidos
- DNI de 8 dígitos
- Fecha en formato DD/MM/AAAA
- Nacionalidad detectada

---

### **2.4 PRUEBA: Formulario Completo** 📋

**Objetivo**: Completar todo el proceso de registro

**Pasos**:
1. **Clic en**: "✅ Continuar"
2. **Seleccionar duración**: "3 horas"
3. **Seleccionar precio**: "S/30"
4. **Seleccionar pago**: "Efectivo"
5. **Seleccionar habitación**: "🟢 Habitación 1"
6. **Agregar observación**: "Cliente habitual"
7. **Confirmar**: "✅ Confirmar y Guardar"

**Resultado esperado final**:
```
✅ Registro exitoso

El cliente ha sido registrado correctamente.
Los datos se han guardado en Google Sheets y la foto en Google Drive.

Usa /nuevo para registrar otro cliente.
```

**✅ Verificar**:
- Proceso fluido sin errores
- Todos los pasos completados
- Mensaje de confirmación recibido

---

### **2.5 PRUEBA: Verificar Google Sheets** 📊

**Objetivo**: Confirmar que los datos se guardaron correctamente

**Pasos**:
1. **Abrir tu Google Sheet**
2. **Verificar nueva fila** con los datos

**Resultado esperado**:
| Fecha | Hora Ingreso | Hora Salida | Habitación | DNI | Nombre | Nacionalidad | Duración | Precio | Pago | Observaciones | Registrado por |
|-------|-------------|-------------|------------|-----|---------|-------------|----------|---------|------|---------------|----------------|
| 2024-XX-XX | 14:30 | 17:30 | 1 | 12345678 | PÉREZ GARCÍA... | PERUANA | 3 horas | S/30 | Efectivo | Cliente habitual | Tu Nombre |

**✅ Verificar**:
- Nueva fila creada
- Todos los campos completos
- Hora de salida calculada automáticamente
- Formato correcto de datos

---

### **2.6 PRUEBA: Verificar Google Drive** 📁

**Objetivo**: Confirmar que la foto se almacenó

**Pasos**:
1. **Abrir tu carpeta** de Google Drive
2. **Buscar archivo** recién creado

**Resultado esperado**:
- Archivo: `DNI_12345678_NOMBRE_20241201_143045.jpg`
- Foto visible y de buena calidad
- Timestamp en el nombre del archivo

**✅ Verificar**:
- Foto subida correctamente
- Nombre único con timestamp
- Archivo accesible

---

### **2.7 PRUEBA: Comando /resumen** 📈

**Objetivo**: Verificar reportes diarios

**Pasos**:
1. Enviar: `/resumen`

**Resultado esperado**:
```
📊 Resumen del día - 2024-12-01

👥 Total de clientes: 1
💰 Ingresos totales: S/30

📋 Registros del día:
• PÉREZ GARCÍA JUAN CARLOS - Hab. 1
```

**✅ Verificar**:
- Contador correcto de clientes
- Suma correcta de ingresos
- Lista de registros del día

---

### **2.8 PRUEBA: Comando /habitaciones** 🏠

**Objetivo**: Verificar disponibilidad de habitaciones

**Pasos**:
1. Enviar: `/habitaciones`

**Resultado esperado**:
```
🏠 Disponibilidad de Habitaciones

🟢 Disponibles:
• Habitación 2
• Habitación 3
• Habitación 4
• Habitación 5
...

🔴 Ocupadas:
• Habitación 1
```

**✅ Verificar**:
- Habitación 1 marcada como ocupada
- Otras habitaciones disponibles
- Estados actualizados correctamente

---

### **2.9 PRUEBA: Comando /ayuda** ❓

**Objetivo**: Verificar información de ayuda

**Pasos**:
1. Enviar: `/ayuda`

**Resultado esperado**:
```
🆘 Ayuda - Bot de Registro de Clientes

Comandos disponibles:
• /start - Iniciar bot
• /nuevo - Registrar nuevo cliente
• /resumen - Ver resumen del día
• /habitaciones - Ver disponibilidad
• /ayuda - Mostrar esta ayuda

Cómo usar:
1. Usa /nuevo o envía una foto del DNI
2. El bot extraerá los datos automáticamente
...
```

**✅ Verificar**: Información completa y clara

---

## **FASE 3: PRUEBAS AVANZADAS** 🔬

### **3.1 PRUEBA: Fotos de Diferentes Calidades** 📷

**Objetivo**: Probar robustez del OCR

**Casos de prueba**:
1. **Foto nítida y frontal** ✅
2. **Foto con ángulo lateral** 📐
3. **Foto ligeramente borrosa** 🌫️
4. **Foto con poca iluminación** 🌙
5. **Foto de DNI venezolano** 🇻🇪
6. **Foto muy grande (>10MB)** 📏

**Para cada caso**:
- Enviar foto al bot
- Verificar que procese correctamente
- Anotar calidad de extracción (1-10)

---

### **3.2 PRUEBA: Opciones Personalizadas** ⚙️

**Objetivo**: Probar funciones personalizables

**Casos**:
1. **Precio personalizado**: "💰 Precio personalizado" → Escribir "S/45"
2. **Habitación personalizada**: "🏠 Otra habitación" → Escribir "Suite 101"
3. **Sin observaciones**: "➡️ Continuar sin observaciones"

---

### **3.3 PRUEBA: Edición de Datos** ✏️

**Objetivo**: Probar corrección de datos extraídos

**Pasos**:
1. Después de OCR, clic en "✏️ Editar datos"
2. Probar editar cada campo:
   - "👤 Editar nombre"
   - "🆔 Editar DNI"
   - "📅 Editar fecha nacimiento"
   - "🌍 Editar nacionalidad"

---

### **3.4 PRUEBA: Flujos de Error** ⚠️

**Objetivo**: Verificar manejo de errores

**Casos**:
1. **Enviar foto que no es DNI** (paisaje, comida, etc.)
2. **Enviar texto** cuando espera foto
3. **Cancelar proceso** a mitad de camino
4. **Reiniciar proceso** varias veces

---

### **3.5 PRUEBA: Múltiples Usuarios** 👥

**Objetivo**: Probar concurrencia

**Pasos**:
1. **Agregar otro Chat ID** a AUTHORIZED_USERS
2. **Registrar cliente** desde primer usuario
3. **Simultáneamente** registrar desde segundo usuario
4. **Verificar** que no se interfieren

---

### **3.6 PRUEBA: Seguridad** 🔐

**Objetivo**: Verificar control de acceso

**Pasos**:
1. **Usuario no autorizado** intenta usar bot
2. **Debe recibir**: "❌ No tienes autorización para usar este bot"

---

## **FASE 4: PRUEBAS DE RENDIMIENTO** ⚡

### **4.1 PRUEBA: Velocidad de OCR** ⏱️

**Medir tiempos**:
- Foto pequeña (<1MB): ~5-10 segundos
- Foto grande (5MB+): ~10-15 segundos
- Foto compleja (ángulo): ~15-20 segundos

### **4.2 PRUEBA: Capacidad de Almacenamiento** 💾

**Verificar límites**:
1. **Google Sheets**: ~1 millón de registros máximo
2. **Google Drive**: Según tu plan (15GB gratis)
3. **OpenAI API**: Según tu plan y créditos

---

## **FASE 5: PRUEBAS DE INTEGRACIÓN** 🔗

### **5.1 PRUEBA: Flujo Completo Repetido** 🔄

**Objetivo**: Registrar múltiples clientes seguidos

**Pasos**:
1. **Registrar Cliente A** (Habitación 1)
2. **Registrar Cliente B** (Habitación 2) 
3. **Registrar Cliente C** (Habitación 3)
4. **Verificar** que todos aparecen en /resumen
5. **Verificar** disponibilidad actualizada en /habitaciones

---

### **5.2 PRUEBA: Recuperación de Errores** 🛠️

**Escenarios**:
1. **Internet intermitente**
2. **OpenAI API temporalmente no disponible**
3. **Google Sheets temporalmente inaccesible**
4. **Google Drive con problemas**

---

## **CHECKLIST FINAL** ✅

### **Funcionalidades Core** 🎯
- [ ] Bot responde a /start
- [ ] OCR extrae datos correctamente
- [ ] Formulario guiado funciona
- [ ] Datos se guardan en Google Sheets
- [ ] Fotos se almacenan en Google Drive
- [ ] Reportes (/resumen) funcionan
- [ ] Disponibilidad (/habitaciones) actualizada
- [ ] Seguridad (solo usuarios autorizados)

### **Funcionalidades Avanzadas** ⭐
- [ ] Maneja fotos de diferentes ángulos
- [ ] Opciones personalizadas funcionan
- [ ] Edición de datos extraídos
- [ ] Manejo robusto de errores
- [ ] Múltiples usuarios concurrentes
- [ ] Rendimiento aceptable (<20seg por OCR)

### **Integraciones** 🔗
- [ ] OpenAI Vision API responde
- [ ] Google Sheets actualiza automáticamente
- [ ] Google Drive almacena fotos
- [ ] Telegram Bot API funciona estable

---

## **MÉTRICAS DE ÉXITO** 📊

### **Precisión OCR** 🎯
- **Excelente**: 90-100% campos correctos
- **Buena**: 70-89% campos correctos  
- **Aceptable**: 50-69% campos correctos
- **Mejorar**: <50% campos correctos

### **Tiempo de Respuesta** ⚡
- **Excelente**: <10 segundos total
- **Bueno**: 10-15 segundos
- **Aceptable**: 15-25 segundos
- **Lento**: >25 segundos

### **Confiabilidad** 🛡️
- **Perfecta**: 100% registros completados
- **Excelente**: 95-99% éxito
- **Buena**: 90-94% éxito
- **Mejorar**: <90% éxito

---

## **PROBLEMAS COMUNES Y SOLUCIONES** 🔧

### **Bot no responde** 🤖
**Posibles causas**:
- Token incorrecto
- Usuario no autorizado  
- Internet/servidores Telegram

**Solución**:
```bash
# Verificar token
python -c "import telegram; bot = telegram.Bot('TU_TOKEN'); print(bot.get_me())"
```

### **OCR falla** 🔍
**Posibles causas**:
- Foto muy borrosa
- OpenAI API sin créditos
- Clave API incorrecta

**Solución**:
- Probar con foto más nítida
- Verificar saldo OpenAI
- Validar clave API

### **No guarda en Sheets** 📊
**Posibles causas**:
- Permisos insuficientes
- ID incorrecto
- Credenciales erróneas

**Solución**:
```bash
# Probar conexión manualmente
python -c "import gspread; gc = gspread.service_account('credentials/hotel-bot-service-account.json'); print('✅ Conectado')"
```

### **No sube a Drive** 📁
**Posibles causas**:
- Primer uso (requiere OAuth)
- Permisos insuficientes
- Carpeta no compartida

**Solución**:
- Primera vez: completar flow OAuth en terminal
- Verificar permisos carpeta Drive

---

## **PRÓXIMOS PASOS** 🚀

Una vez que todas las pruebas pasen exitosamente:

1. **Deploy en producción** (Heroku, Railway, VPS)
2. **Monitoreo continuo** con logs
3. **Capacitación del personal** del hotel
4. **Backup regular** de datos
5. **Actualización periódica** de dependencias

**¡Tu HotelBot está listo para revolucionar el registro de clientes! 🏨✨** 