# 🚀 GUÍA RÁPIDA DE PRUEBAS - HotelBot

## **PRUEBAS SECUENCIALES (15 minutos total)**

### **PRUEBA 1: Inicialización (2 min)** 🤖
```bash
python start_bot.py
```
**Resultado esperado**: Todos los checks ✅ y bot iniciado

---

### **PRUEBA 2: Comando /start (30 seg)** 👋
**Telegram**: `/start`

**Debe mostrar**:
```
🏨 Bot de Registro de Clientes

¡Hola! Soy el bot del hotel...

Comandos disponibles:
• /nuevo - Registrar nuevo cliente
• /resumen - Ver resumen del día
• /habitaciones - Ver disponibilidad
• /ayuda - Obtener ayuda
```

---

### **PRUEBA 3: Registro Completo (8 min)** 📝

#### **3.1 Iniciar registro**
**Telegram**: `/nuevo`

#### **3.2 Enviar foto de DNI**
- Enviar cualquier foto de DNI clara
- **Esperar**: 10-20 segundos (procesamiento OCR)
- **Resultado**: Datos extraídos automáticamente

#### **3.3 Completar formulario**
1. **Clic**: "✅ Continuar" 
2. **Duración**: "3 horas"
3. **Precio**: "S/30"  
4. **Pago**: "Efectivo"
5. **Habitación**: "🟢 Habitación 1"
6. **Observación**: "Cliente de prueba"
7. **Confirmar**: "✅ Confirmar y Guardar"

**Resultado final**: "✅ Registro exitoso"

---

### **PRUEBA 4: Verificar Almacenamiento (2 min)** 💾

#### **4.1 Google Sheets** 
- Abrir tu hoja de cálculo
- **Verificar**: Nueva fila con todos los datos
- **Campos**: Fecha, hora, habitación, DNI, nombre, etc.

#### **4.2 Google Drive**
- Abrir tu carpeta de Drive  
- **Verificar**: Nueva foto con nombre único
- **Formato**: `DNI_12345678_NOMBRE_timestamp.jpg`

---

### **PRUEBA 5: Comandos de Reporte (2 min)** 📊

#### **5.1 Resumen diario**
**Telegram**: `/resumen`
```
📊 Resumen del día - 2024-XX-XX

👥 Total de clientes: 1
💰 Ingresos totales: S/30

📋 Registros del día:
• NOMBRE CLIENTE - Hab. 1
```

#### **5.2 Disponibilidad**
**Telegram**: `/habitaciones`
```
🏠 Disponibilidad de Habitaciones

🟢 Disponibles:
• Habitación 2, 3, 4, 5...

🔴 Ocupadas:  
• Habitación 1
```

#### **5.3 Ayuda**
**Telegram**: `/ayuda`
**Resultado**: Manual completo del bot

---

## **CHECKLIST DE ÉXITO** ✅

**Funcionalidades Core**:
- [ ] Bot responde a todos los comandos
- [ ] OCR extrae datos correctamente (70%+ precisión)
- [ ] Formulario se completa sin errores
- [ ] Datos aparecen en Google Sheets
- [ ] Fotos se almacenan en Google Drive  
- [ ] Reportes muestran información actualizada

**Indicadores de Calidad**:
- [ ] Tiempo de respuesta OCR < 20 segundos
- [ ] Interfaz intuitiva con emojis y botones
- [ ] Manejo robusto de errores
- [ ] Solo usuarios autorizados pueden usar el bot

---

## **TESTS AVANZADOS OPCIONALES** 🔬

### **Test de Robustez OCR** 📷
Probar con fotos de diferentes calidades:
- Foto nítida frontal ⭐⭐⭐⭐⭐
- Foto con ángulo lateral ⭐⭐⭐⭐
- Foto ligeramente borrosa ⭐⭐⭐
- Foto con poca luz ⭐⭐
- DNI de otros países (Venezuela, Colombia) ⭐⭐⭐⭐

### **Test de Opciones Personalizadas** ⚙️
- **Precio personalizado**: "S/45"
- **Habitación personalizada**: "Suite VIP"
- **Sin observaciones**: Dejar vacío

### **Test de Concurrencia** 👥
- Dos usuarios registrando simultáneamente
- Verificar que no se interfieren
- Comprobar integridad de datos

### **Test de Seguridad** 🔐
- Usuario no autorizado intenta usar bot
- Debe recibir mensaje de acceso denegado

---

## **PROBLEMAS COMUNES Y SOLUCIONES** ⚠️

### **Bot no responde**
```bash
# Verificar token
python -c "import telegram; bot = telegram.Bot('TU_TOKEN'); print(bot.get_me())"
```

### **OCR no funciona**
- Verificar créditos OpenAI: https://platform.openai.com/usage
- Probar con foto más nítida
- Validar API key en .env

### **No guarda en Sheets**
- Verificar permisos de la hoja (debe estar compartida con service account)
- Validar GOOGLE_SHEETS_SPREADSHEET_ID

### **No sube a Drive**  
- Primera vez: completar OAuth flow en terminal
- Verificar permisos de carpeta Drive

---

## **COMANDOS DE DIAGNÓSTICO** 🔧

### **Verificar configuración completa**
```bash
python test_bot.py
```

### **Probar solo OpenAI**
```bash
python -c "
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Test'}],
    max_tokens=5
)
print('✅ OpenAI funciona')
"
```

### **Probar solo Google Sheets**
```bash
python -c "
import gspread
from google.oauth2.service_account import Credentials
from config import Config

creds = Credentials.from_service_account_file(
    Config.GOOGLE_APPLICATION_CREDENTIALS,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(Config.GOOGLE_SHEETS_SPREADSHEET_ID)
print(f'✅ Conectado a: {sheet.title}')
"
```

---

## **MÉTRICAS DE RENDIMIENTO** 📈

### **Tiempos Esperados**
- **Inicialización del bot**: 3-5 segundos
- **Procesamiento OCR**: 5-20 segundos (dependiendo de la imagen)
- **Guardado en Sheets**: 1-3 segundos
- **Subida a Drive**: 2-5 segundos
- **Respuesta a comandos**: <1 segundo

### **Precisión OCR por Tipo de Imagen**
- **Foto perfecta (frontal, nítida)**: 95-100%
- **Foto buena (ligero ángulo)**: 85-95%
- **Foto regular (borrosa/ángulo)**: 70-85%
- **Foto mala (muy borrosa/oscura)**: 50-70%

### **Capacidades del Sistema**
- **Google Sheets**: ~1 millón de filas máximo
- **Google Drive**: 15GB gratis (después según plan)
- **OpenAI API**: Según créditos disponibles
- **Telegram Bot**: Sin límites prácticos

---

## **¡LISTO PARA PRODUCCIÓN!** 🚀

Si todas las pruebas pasan exitosamente, tu HotelBot está **100% funcional** y listo para:

1. **Deployment** en servidores (Heroku, Railway, VPS)
2. **Uso en producción** por el personal del hotel  
3. **Escalamiento** para manejar múltiples usuarios
4. **Monitoreo** con logs automáticos

**Tu bot es una solución profesional completa que reemplaza efectivamente el registro manual con papel. ¡Excelente trabajo!** 🏨✨ 