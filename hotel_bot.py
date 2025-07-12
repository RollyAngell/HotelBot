import logging
import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

from config import Config
from utils.ocr_processor import OCRProcessor
from utils.sheets_manager import SheetsManager
from utils.drive_manager import DriveManager

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HotelBot:
    """Bot de Telegram para registro de clientes de hotel"""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.sheets_manager = SheetsManager()
        self.drive_manager = DriveManager()
        self.timezone = pytz.timezone(Config.TIMEZONE)
        
        # Estados del bot
        self.user_states = {}
        self.client_data = {}
    
    def is_authorized(self, user_id):
        """Verificar si el usuario está autorizado"""
        return user_id in Config.AUTHORIZED_USERS
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text(
                "❌ No tienes autorización para usar este bot.\n"
                "Contacta al administrador del sistema."
            )
            return
        
        welcome_message = (
            "🏨 *Bot de Registro de Clientes*\n\n"
            "¡Hola! Soy el bot del hotel para registrar clientes.\n\n"
            "Comandos disponibles:\n"
            "• /nuevo - Registrar nuevo cliente\n"
            "• /resumen - Ver resumen del día\n"
            "• /habitaciones - Ver disponibilidad\n"
            "• /ayuda - Obtener ayuda\n\n"
            "Para comenzar, envía una foto del DNI del cliente o usa /nuevo"
        )
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def nuevo_cliente(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /nuevo para iniciar registro"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        # Inicializar estado del usuario
        self.user_states[user_id] = 'waiting_dni_photo'
        self.client_data[user_id] = {
            'hora_ingreso': datetime.now(self.timezone).strftime('%H:%M'),
            'fecha': datetime.now(self.timezone).strftime('%Y-%m-%d'),
            'registrado_por': update.effective_user.first_name or "Usuario"
        }
        
        await update.message.reply_text(
            "📷 *Nuevo Cliente*\n\n"
            "Por favor, envía una foto del DNI del cliente para comenzar el registro.\n"
            "Asegúrate de que la imagen sea clara y legible.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar fotos enviadas"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        # Verificar si estamos esperando foto de DNI
        if self.user_states.get(user_id) != 'waiting_dni_photo':
            await update.message.reply_text(
                "❓ No estoy esperando una foto en este momento.\n"
                "Usa /nuevo para comenzar un nuevo registro."
            )
            return
        
        # Mostrar mensaje de procesamiento
        processing_msg = await update.message.reply_text(
            "⏳ Procesando imagen del DNI...\n"
            "Esto puede tomar unos segundos."
        )
        
        try:
            # Obtener la imagen
            photo = update.message.photo[-1]  # Mejor calidad
            file = await context.bot.get_file(photo.file_id)
            
            # Descargar imagen
            image_bytes = await file.download_as_bytearray()
            
            # Redimensionar si es necesario
            image_bytes = self.ocr_processor.resize_image_if_needed(bytes(image_bytes))
            
            # Procesar OCR
            extracted_text = self.ocr_processor.extract_text_from_image(image_bytes)
            dni_data = self.ocr_processor.extract_dni_data(extracted_text)
            
            # Guardar datos extraídos
            self.client_data[user_id].update(dni_data)
            
            # Subir foto a Google Drive
            drive_result = self.drive_manager.upload_dni_photo(
                image_bytes, 
                dni_data.get('dni', 'unknown'),
                dni_data.get('nombre')
            )
            
            if drive_result:
                self.client_data[user_id]['foto_drive_id'] = drive_result['file_id']
                self.client_data[user_id]['foto_url'] = drive_result['web_view_link']
            
            # Eliminar mensaje de procesamiento
            await processing_msg.delete()
            
            # Mostrar datos extraídos
            await self.show_extracted_data(update, user_id)
            
        except Exception as e:
            logger.error(f"Error al procesar foto: {str(e)}")
            await processing_msg.edit_text(
                "❌ Error al procesar la imagen del DNI.\n"
                "Por favor, intenta con otra foto más clara."
            )
    
    async def show_extracted_data(self, update: Update, user_id: int):
        """Mostrar datos extraídos del DNI"""
        data = self.client_data[user_id]
        
        message = "📋 *Datos extraídos del DNI:*\n\n"
        
        if data.get('nombre'):
            message += f"👤 **Nombre:** {data['nombre']}\n"
        else:
            message += f"👤 **Nombre:** ❌ No detectado\n"
        
        if data.get('dni'):
            message += f"🆔 **DNI:** {data['dni']}\n"
        else:
            message += f"🆔 **DNI:** ❌ No detectado\n"
        
        if data.get('fecha_nacimiento'):
            message += f"📅 **Fecha Nacimiento:** {data['fecha_nacimiento']}\n"
        else:
            message += f"📅 **Fecha Nacimiento:** ❌ No detectado\n"
        
        if data.get('nacionalidad'):
            message += f"🌍 **Nacionalidad:** {data['nacionalidad']}\n"
        else:
            message += f"🌍 **Nacionalidad:** ❌ No detectado\n"
        
        message += "\n"
        
        # Botones de acción
        keyboard = [
            [InlineKeyboardButton("✅ Continuar", callback_data="continue_registration")],
            [InlineKeyboardButton("✏️ Editar datos", callback_data="edit_data")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar callbacks de botones"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not self.is_authorized(user_id):
            await query.edit_message_text("❌ No tienes autorización para usar este bot.")
            return
        
        if query.data == "continue_registration":
            await self.ask_duration(query, user_id)
        elif query.data == "edit_data":
            await self.edit_data_menu(query, user_id)
        elif query.data == "cancel_registration":
            await self.cancel_registration(query, user_id)
        elif query.data.startswith("duration_"):
            await self.handle_duration_selection(query, user_id)
        elif query.data.startswith("price_"):
            await self.handle_price_selection(query, user_id)
        elif query.data.startswith("payment_"):
            await self.handle_payment_selection(query, user_id)
        elif query.data.startswith("room_"):
            await self.handle_room_selection(query, user_id)
        elif query.data == "confirm_registration":
            await self.confirm_registration(query, user_id)
        elif query.data == "edit_observations":
            await self.ask_observations(query, user_id)
    
    async def ask_duration(self, query, user_id):
        """Preguntar duración de estancia"""
        self.user_states[user_id] = 'selecting_duration'
        
        keyboard = []
        for duration in Config.DURACION_OPCIONES:
            keyboard.append([InlineKeyboardButton(duration, callback_data=f"duration_{duration}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⏰ *¿Cuántas horas usará el cliente?*\n\n"
            "Selecciona la duración de la estancia:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_duration_selection(self, query, user_id):
        """Manejar selección de duración"""
        duration = query.data.replace("duration_", "")
        self.client_data[user_id]['duracion'] = duration
        
        # Calcular hora de salida estimada
        current_time = datetime.now(self.timezone)
        
        if duration == "2 horas":
            exit_time = current_time + timedelta(hours=2)
        elif duration == "3 horas":
            exit_time = current_time + timedelta(hours=3)
        elif duration == "noche":
            # Noche hasta las 8 AM del día siguiente
            exit_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        self.client_data[user_id]['hora_salida_estimada'] = exit_time.strftime('%H:%M')
        
        await self.ask_price(query, user_id)
    
    async def ask_price(self, query, user_id):
        """Preguntar precio cobrado"""
        self.user_states[user_id] = 'selecting_price'
        
        keyboard = []
        for price in Config.PRECIO_OPCIONES:
            keyboard.append([InlineKeyboardButton(price, callback_data=f"price_{price}")])
        
        # Opción de precio personalizado
        keyboard.append([InlineKeyboardButton("💰 Precio personalizado", callback_data="price_custom")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💰 *¿Precio cobrado?*\n\n"
            "Selecciona el precio cobrado al cliente:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_price_selection(self, query, user_id):
        """Manejar selección de precio"""
        if query.data == "price_custom":
            self.user_states[user_id] = 'waiting_custom_price'
            await query.edit_message_text(
                "💰 *Precio personalizado*\n\n"
                "Escribe el precio cobrado (ejemplo: S/35, $20, etc.):"
            )
            return
        
        price = query.data.replace("price_", "")
        self.client_data[user_id]['precio'] = price
        
        await self.ask_payment_method(query, user_id)
    
    async def ask_payment_method(self, query, user_id):
        """Preguntar forma de pago"""
        self.user_states[user_id] = 'selecting_payment'
        
        keyboard = []
        for payment in Config.PAGO_OPCIONES:
            keyboard.append([InlineKeyboardButton(payment, callback_data=f"payment_{payment}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💳 *¿Forma de pago?*\n\n"
            "Selecciona la forma de pago utilizada:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_payment_selection(self, query, user_id):
        """Manejar selección de forma de pago"""
        payment = query.data.replace("payment_", "")
        self.client_data[user_id]['forma_pago'] = payment
        
        await self.ask_room(query, user_id)
    
    async def ask_room(self, query, user_id):
        """Preguntar habitación"""
        self.user_states[user_id] = 'selecting_room'
        
        # Obtener disponibilidad de habitaciones
        availability = self.sheets_manager.get_room_availability()
        
        keyboard = []
        
        # Mostrar habitaciones disponibles
        for room in availability['available']:
            keyboard.append([InlineKeyboardButton(f"🟢 Habitación {room}", callback_data=f"room_{room}")])
        
        # Mostrar habitaciones ocupadas
        for room in availability['occupied']:
            keyboard.append([InlineKeyboardButton(f"🔴 Habitación {room} (ocupada)", callback_data=f"room_{room}_occupied")])
        
        # Opción de habitación personalizada
        keyboard.append([InlineKeyboardButton("🏠 Otra habitación", callback_data="room_custom")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏠 *¿Qué habitación usará el cliente?*\n\n"
            "🟢 = Disponible | 🔴 = Ocupada\n\n"
            "Selecciona la habitación:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_room_selection(self, query, user_id):
        """Manejar selección de habitación"""
        if query.data == "room_custom":
            self.user_states[user_id] = 'waiting_custom_room'
            await query.edit_message_text(
                "🏠 *Habitación personalizada*\n\n"
                "Escribe el número o nombre de la habitación:"
            )
            return
        elif query.data.endswith("_occupied"):
            await query.answer("⚠️ Esta habitación está ocupada", show_alert=True)
            return
        
        room = query.data.replace("room_", "")
        self.client_data[user_id]['habitacion'] = room
        
        await self.ask_observations(query, user_id)
    
    async def ask_observations(self, query, user_id):
        """Preguntar observaciones"""
        self.user_states[user_id] = 'waiting_observations'
        
        keyboard = [
            [InlineKeyboardButton("📝 Agregar observación", callback_data="add_observation")],
            [InlineKeyboardButton("➡️ Continuar sin observaciones", callback_data="no_observations")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📝 *¿Alguna observación?*\n\n"
            "Puedes agregar comentarios adicionales sobre el cliente o la reserva:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar entradas de texto"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        state = self.user_states.get(user_id)
        
        if state == 'waiting_custom_price':
            self.client_data[user_id]['precio'] = update.message.text
            self.user_states[user_id] = 'selecting_payment'
            await self.ask_payment_method_after_custom_price(update, user_id)
        
        elif state == 'waiting_custom_room':
            self.client_data[user_id]['habitacion'] = update.message.text
            self.user_states[user_id] = 'waiting_observations'
            await self.ask_observations_after_custom_room(update, user_id)
        
        elif state == 'waiting_observations':
            self.client_data[user_id]['observaciones'] = update.message.text
            await self.show_final_summary(update, user_id)
    
    async def show_final_summary(self, update: Update, user_id: int):
        """Mostrar resumen final antes de guardar"""
        data = self.client_data[user_id]
        
        message = "📋 *Resumen del Registro*\n\n"
        message += f"👤 **Cliente:** {data.get('nombre', 'N/A')}\n"
        message += f"🆔 **DNI:** {data.get('dni', 'N/A')}\n"
        message += f"🏠 **Habitación:** {data.get('habitacion', 'N/A')}\n"
        message += f"🕐 **Ingreso:** {data.get('hora_ingreso', 'N/A')}\n"
        message += f"🕐 **Salida estimada:** {data.get('hora_salida_estimada', 'N/A')}\n"
        message += f"💰 **Precio:** {data.get('precio', 'N/A')}\n"
        message += f"💳 **Pago:** {data.get('forma_pago', 'N/A')}\n"
        message += f"📝 **Observaciones:** {data.get('observaciones', 'Ninguna')}\n"
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar y Guardar", callback_data="confirm_registration")],
            [InlineKeyboardButton("✏️ Editar", callback_data="edit_data")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def confirm_registration(self, query, user_id):
        """Confirmar y guardar registro"""
        try:
            # Guardar en Google Sheets
            success = self.sheets_manager.save_client_data(self.client_data[user_id])
            
            if success:
                await query.edit_message_text(
                    "✅ *Registro exitoso*\n\n"
                    "El cliente ha sido registrado correctamente.\n"
                    "Los datos se han guardado en Google Sheets y la foto en Google Drive.\n\n"
                    "Usa /nuevo para registrar otro cliente.",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Limpiar datos del usuario
                self.user_states.pop(user_id, None)
                self.client_data.pop(user_id, None)
                
            else:
                await query.edit_message_text(
                    "❌ *Error al guardar*\n\n"
                    "Hubo un problema al guardar los datos.\n"
                    "Por favor, intenta nuevamente."
                )
                
        except Exception as e:
            logger.error(f"Error al confirmar registro: {str(e)}")
            await query.edit_message_text(
                "❌ *Error del sistema*\n\n"
                "Ocurrió un error inesperado. Contacta al administrador."
            )
    
    async def cancel_registration(self, query, user_id):
        """Cancelar registro"""
        self.user_states.pop(user_id, None)
        self.client_data.pop(user_id, None)
        
        await query.edit_message_text(
            "❌ *Registro cancelado*\n\n"
            "El registro ha sido cancelado.\n"
            "Usa /nuevo para comenzar un nuevo registro."
        )
    
    async def resumen_diario(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /resumen - mostrar resumen del día"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        try:
            summary = self.sheets_manager.get_daily_summary()
            
            message = f"📊 *Resumen del día - {summary['date']}*\n\n"
            message += f"👥 **Total de clientes:** {summary['total_clients']}\n"
            message += f"💰 **Ingresos totales:** S/{summary['total_revenue']}\n\n"
            
            if summary['records']:
                message += "📋 **Registros del día:**\n"
                for record in summary['records'][-5:]:  # Últimos 5 registros
                    message += f"• {record.get('Nombre', 'N/A')} - Hab. {record.get('Habitación', 'N/A')}\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error al obtener resumen: {str(e)}")
            await update.message.reply_text("❌ Error al obtener el resumen diario.")
    
    async def ver_habitaciones(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /habitaciones - ver disponibilidad"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        try:
            availability = self.sheets_manager.get_room_availability()
            
            message = "🏠 *Disponibilidad de Habitaciones*\n\n"
            
            if availability['available']:
                message += "🟢 **Disponibles:**\n"
                for room in availability['available']:
                    message += f"• Habitación {room}\n"
            else:
                message += "🟢 **Disponibles:** Ninguna\n"
            
            message += "\n"
            
            if availability['occupied']:
                message += "🔴 **Ocupadas:**\n"
                for room in availability['occupied']:
                    message += f"• Habitación {room}\n"
            else:
                message += "🔴 **Ocupadas:** Ninguna\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error al obtener disponibilidad: {str(e)}")
            await update.message.reply_text("❌ Error al obtener la disponibilidad.")
    
    async def ayuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ayuda"""
        help_message = (
            "🆘 *Ayuda - Bot de Registro de Clientes*\n\n"
            "**Comandos disponibles:**\n"
            "• /start - Iniciar bot\n"
            "• /nuevo - Registrar nuevo cliente\n"
            "• /resumen - Ver resumen del día\n"
            "• /habitaciones - Ver disponibilidad\n"
            "• /ayuda - Mostrar esta ayuda\n\n"
            "**Cómo usar:**\n"
            "1. Usa /nuevo o envía una foto del DNI\n"
            "2. El bot extraerá los datos automáticamente\n"
            "3. Completa la información solicitada\n"
            "4. Confirma el registro\n\n"
            "**Soporte:**\n"
            "Si tienes problemas, contacta al administrador."
        )
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    def run(self):
        """Ejecutar el bot"""
        try:
            # Validar configuración
            Config.validate_config()
            
            # Crear aplicación
            application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            
            # Agregar manejadores
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("nuevo", self.nuevo_cliente))
            application.add_handler(CommandHandler("resumen", self.resumen_diario))
            application.add_handler(CommandHandler("habitaciones", self.ver_habitaciones))
            application.add_handler(CommandHandler("ayuda", self.ayuda))
            
            application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
            application.add_handler(CallbackQueryHandler(self.handle_callback))
            
            # Iniciar bot
            logger.info("Bot iniciado exitosamente")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error al iniciar bot: {str(e)}")
            raise

if __name__ == "__main__":
    bot = HotelBot()
    bot.run() 