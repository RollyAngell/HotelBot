import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

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
    
    def start(self, update: Update, context: CallbackContext):
        """Comando /start"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text(
                "❌ No tienes autorización para usar este bot.\n"
                "Contacta al administrador del sistema."
            )
            return
        
        welcome_message = (
            "🏨 *Bot de Registro de Clientes*\n\n"
            "¡Hola! Soy el bot del hotel para registrar clientes.\n\n"
            "✨ *Nuevas mejoras:*\n"
            "• Procesamiento avanzado de imágenes de DNI\n"
            "• Funciona con fotos desde cualquier ángulo\n"
            "• Reconocimiento mejorado de texto\n\n"
            "Comandos disponibles:\n"
            "• /nuevo - Registrar nuevo cliente\n"
            "• /resumen - Ver resumen del día\n"
            "• /habitaciones - Ver disponibilidad\n"
            "• /ayuda - Obtener ayuda\n\n"
            "Para comenzar, envía una foto del DNI del cliente o usa /nuevo"
        )
        
        update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    def nuevo_cliente(self, update: Update, context: CallbackContext):
        """Comando /nuevo para iniciar registro"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        # Inicializar estado del usuario
        self.user_states[user_id] = 'waiting_dni_photo'
        self.client_data[user_id] = {
            'hora_ingreso': datetime.now(self.timezone).strftime('%H:%M'),
            'fecha': datetime.now(self.timezone).strftime('%Y-%m-%d'),
            'registrado_por': update.effective_user.first_name or "Usuario"
        }
        
        update.message.reply_text(
            "📷 *Nuevo Cliente*\n\n"
            "Por favor, envía una foto del DNI del cliente para comenzar el registro.\n\n"
            "✅ *Consejos para mejores resultados:*\n"
            "• La foto puede ser tomada desde cualquier ángulo\n"
            "• No importa si está ligeramente inclinada\n"
            "• Asegúrate de que el texto sea visible\n"
            "• El bot automáticamente mejorará la imagen\n"
            "• Si la primera foto no funciona, puedes intentar con otra",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def handle_photo(self, update: Update, context: CallbackContext):
        """Manejar fotos enviadas"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        # Verificar si estamos esperando foto de DNI
        if self.user_states.get(user_id) != 'waiting_dni_photo':
            update.message.reply_text(
                "❓ No estoy esperando una foto en este momento.\n"
                "Usa /nuevo para comenzar un nuevo registro."
            )
            return
        
        # Mostrar mensaje de procesamiento
        processing_msg = update.message.reply_text(
            "⏳ *Procesando imagen del DNI...*\n\n"
            "🔍 Analizando imagen con IA avanzada\n"
            "🖼️ Mejorando calidad automáticamente\n"
            "📝 Extrayendo datos del documento\n\n"
            "Esto puede tomar unos segundos.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Obtener la imagen
            photo = update.message.photo[-1]  # Mejor calidad
            file = context.bot.get_file(photo.file_id)
            
            # Descargar imagen
            image_bytes = file.download_as_bytearray()
            
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
            context.bot.delete_message(chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)
            
            # Verificar calidad de extracción y mostrar mensaje apropiado
            extracted_fields = sum(1 for field in ['nombre', 'dni', 'fecha_nacimiento', 'nacionalidad'] 
                                 if dni_data.get(field))
            
            if extracted_fields >= 3:
                update.message.reply_text("✅ *¡Excelente!* Datos extraídos correctamente", parse_mode=ParseMode.MARKDOWN)
            elif extracted_fields >= 2:
                update.message.reply_text("✅ *¡Bien!* La mayoría de datos fueron extraídos", parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text("⚠️ *Extracción parcial* - Algunos datos pueden necesitar corrección", parse_mode=ParseMode.MARKDOWN)
            
            # Mostrar datos extraídos
            self.show_extracted_data(update, user_id)
            
        except Exception as e:
            logger.error(f"Error al procesar foto: {str(e)}")
            context.bot.edit_message_text(
                text="❌ Error al procesar la imagen del DNI.\nPor favor, intenta con otra foto más clara.",
                chat_id=processing_msg.chat.id,
                message_id=processing_msg.message_id
            )
    
    def show_extracted_data(self, update: Update, user_id: int):
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
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def handle_callback(self, update: Update, context: CallbackContext):
        """Manejar callbacks de botones"""
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        
        if not self.is_authorized(user_id):
            query.edit_message_text("❌ No tienes autorización para usar este bot.")
            return
        
        if query.data == "continue_registration":
            self.ask_duration(query, user_id)
        elif query.data == "edit_data":
            self.edit_data_menu(query, user_id)
        elif query.data == "cancel_registration":
            self.cancel_registration(query, user_id)
        elif query.data == "restart_registration":
            self.restart_registration(query, user_id)
        elif query.data.startswith("duration_"):
            self.handle_duration_selection(query, user_id)
        elif query.data.startswith("price_"):
            self.handle_price_selection(query, user_id)
        elif query.data.startswith("payment_"):
            self.handle_payment_selection(query, user_id)
        elif query.data.startswith("room_"):
            self.handle_room_selection(query, user_id)
        elif query.data == "confirm_registration":
            self.confirm_registration(query, user_id)
        elif query.data == "edit_observations":
            self.ask_observations(query, user_id)
        elif query.data == "add_observation":
            self.prompt_observation(query, user_id)
        elif query.data == "no_observations":
            self.handle_no_observations(query, user_id)
    
    def ask_duration(self, query, user_id):
        """Preguntar duración de estancia"""
        self.user_states[user_id] = 'selecting_duration'
        
        keyboard = []
        for duration in Config.DURACION_OPCIONES:
            keyboard.append([InlineKeyboardButton(duration, callback_data=f"duration_{duration}")])
        
        keyboard.append([InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "⏰ *¿Cuántas horas usará el cliente?*\n\n"
            "Selecciona la duración de la estancia:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def handle_duration_selection(self, query, user_id):
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
        
        self.ask_price(query, user_id)
    
    def ask_price(self, query, user_id):
        """Preguntar precio cobrado"""
        self.user_states[user_id] = 'selecting_price'
        
        keyboard = []
        for price in Config.PRECIO_OPCIONES:
            keyboard.append([InlineKeyboardButton(price, callback_data=f"price_{price}")])
        
        # Opción de precio personalizado
        keyboard.append([InlineKeyboardButton("💰 Precio personalizado", callback_data="price_custom")])
        keyboard.append([InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "💰 *¿Precio cobrado?*\n\n"
            "Selecciona el precio cobrado al cliente:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def handle_price_selection(self, query, user_id):
        """Manejar selección de precio"""
        if query.data == "price_custom":
            self.user_states[user_id] = 'waiting_custom_price'
            query.edit_message_text(
                "💰 *Precio personalizado*\n\n"
                "Escribe el precio cobrado (ejemplo: S/35, $20, etc.):"
            )
            return
        
        price = query.data.replace("price_", "")
        self.client_data[user_id]['precio'] = price
        
        self.ask_payment_method(query, user_id)
    
    def ask_payment_method(self, query, user_id):
        """Preguntar forma de pago"""
        self.user_states[user_id] = 'selecting_payment'
        
        keyboard = []
        for payment in Config.PAGO_OPCIONES:
            keyboard.append([InlineKeyboardButton(payment, callback_data=f"payment_{payment}")])
        
        keyboard.append([InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "💳 *¿Forma de pago?*\n\n"
            "Selecciona la forma de pago utilizada:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def handle_payment_selection(self, query, user_id):
        """Manejar selección de forma de pago"""
        payment = query.data.replace("payment_", "")
        self.client_data[user_id]['forma_pago'] = payment
        
        self.ask_room(query, user_id)
    
    def ask_room(self, query, user_id):
        """Preguntar habitación"""
        self.user_states[user_id] = 'selecting_room'
        
        # Obtener disponibilidad de habitaciones
        try:
            availability = self.sheets_manager.get_room_availability()
        except Exception:
            # Si hay error, usar habitaciones por defecto
            availability = {'available': ['1','2','3','4','5'], 'occupied': []}
        
        keyboard = []
        
        # Mostrar habitaciones disponibles
        if availability['available']:
            # Convertir a strings y ordenar
            available_rooms = [str(room) for room in availability['available']]
            available_rooms.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
            
            for room in available_rooms:
                keyboard.append([InlineKeyboardButton(f"🟢 Habitación {room}", callback_data=f"room_{room}")])
        
        # Mostrar habitaciones ocupadas solo como información (no seleccionables)
        if availability['occupied']:
            occupied_rooms = [str(room) for room in availability['occupied']]
            occupied_rooms.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
            
            for room in occupied_rooms:
                keyboard.append([InlineKeyboardButton(f"🔴 Habitación {room} (ocupada)", callback_data=f"room_info_{room}")])
        
        # Opción de habitación personalizada
        keyboard.append([InlineKeyboardButton("🏠 Otra habitación", callback_data="room_custom")])
        keyboard.append([InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "🏠 *¿Qué habitación usará el cliente?*\n\n"
            "🟢 = Disponible | 🔴 = Ocupada\n\n"
            "Selecciona la habitación:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def handle_room_selection(self, query, user_id):
        """Manejar selección de habitación"""
        if query.data == "room_custom":
            self.user_states[user_id] = 'waiting_custom_room'
            query.edit_message_text(
                "🏠 *Habitación personalizada*\n\n"
                "Escribe el número o nombre de la habitación:"
            )
            return
        elif query.data.startswith("room_info_"):
            query.answer("⚠️ Esta habitación está ocupada", show_alert=True)
            return
        
        room = query.data.replace("room_", "")
        self.client_data[user_id]['habitacion'] = room
        
        self.ask_observations(query, user_id)
    
    def ask_observations(self, query, user_id):
        """Preguntar observaciones"""
        self.user_states[user_id] = 'waiting_observations'
        
        keyboard = [
            [InlineKeyboardButton("📝 Agregar observación", callback_data="add_observation")],
            [InlineKeyboardButton("➡️ Continuar sin observaciones", callback_data="no_observations")],
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "📝 *¿Alguna observación?*\n\n"
            "Puedes agregar comentarios adicionales sobre el cliente o la reserva:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def handle_text_input(self, update: Update, context: CallbackContext):
        """Manejar entradas de texto"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("❌ No tienes autorización para usar este bot.")
            return
        
        state = self.user_states.get(user_id)
        
        if state == 'waiting_custom_price':
            self.client_data[user_id]['precio'] = update.message.text
            self.user_states[user_id] = 'selecting_payment'
            self.ask_payment_method_after_custom_price(update, user_id)
        
        elif state == 'waiting_custom_room':
            self.client_data[user_id]['habitacion'] = update.message.text
            self.user_states[user_id] = 'waiting_observations'
            self.ask_observations_after_custom_room(update, user_id)
        
        elif state == 'waiting_observations':
            self.client_data[user_id]['observaciones'] = update.message.text
            self.show_final_summary(update, user_id)
    
    def ask_payment_method_after_custom_price(self, update: Update, user_id: int):
        """Preguntar forma de pago después de precio personalizado"""
        self.user_states[user_id] = 'selecting_payment'
        
        keyboard = []
        for payment in Config.PAGO_OPCIONES:
            keyboard.append([InlineKeyboardButton(payment, callback_data=f"payment_{payment}")])
        
        keyboard.append([InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "💳 *¿Forma de pago?*\n\n"
            "Selecciona la forma de pago utilizada:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def ask_observations_after_custom_room(self, update: Update, user_id: int):
        """Preguntar observaciones después de habitación personalizada"""
        self.user_states[user_id] = 'waiting_observations'
        
        keyboard = [
            [InlineKeyboardButton("📝 Agregar observación", callback_data="add_observation")],
            [InlineKeyboardButton("➡️ Continuar sin observaciones", callback_data="no_observations")],
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "📝 *¿Alguna observación?*\n\n"
            "Puedes agregar comentarios adicionales sobre el cliente o la reserva:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def show_final_summary(self, update: Update, user_id: int):
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
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def prompt_observation(self, query, user_id):
        """Solicitar que escriba una observación"""
        self.user_states[user_id] = 'waiting_observations'
        
        query.edit_message_text(
            "📝 *Agregar observación*\n\n"
            "Escribe tu observación sobre el cliente o la reserva:"
        )
    
    def handle_no_observations(self, query, user_id):
        """Continuar sin observaciones"""
        self.client_data[user_id]['observaciones'] = ''
        self.show_final_summary_from_query(query, user_id)
    
    def show_final_summary_from_query(self, query, user_id):
        """Mostrar resumen final desde callback query"""
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
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def edit_data_menu(self, query, user_id):
        """Mostrar menú para editar datos"""
        keyboard = [
            [InlineKeyboardButton("👤 Editar nombre", callback_data="edit_name")],
            [InlineKeyboardButton("🆔 Editar DNI", callback_data="edit_dni")],
            [InlineKeyboardButton("📅 Editar fecha nacimiento", callback_data="edit_birthdate")],
            [InlineKeyboardButton("🌍 Editar nacionalidad", callback_data="edit_nationality")],
            [InlineKeyboardButton("✅ Continuar registro", callback_data="continue_registration")],
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart_registration")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_registration")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "✏️ *Editar datos*\n\n"
            "¿Qué dato deseas editar?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def restart_registration(self, query, user_id):
        """Reiniciar el proceso de registro"""
        self.user_states.pop(user_id, None)
        self.client_data.pop(user_id, None)
        
        query.edit_message_text(
            "🔄 *Proceso reiniciado*\n\n"
            "El registro ha sido reiniciado.\n"
            "Usa /nuevo para comenzar un nuevo registro o envía una foto del DNI.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def confirm_registration(self, query, user_id):
        """Confirmar y guardar registro"""
        try:
            # Guardar en Google Sheets
            success = self.sheets_manager.save_client_data(self.client_data[user_id])
            
            if success:
                query.edit_message_text(
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
                query.edit_message_text(
                    "❌ *Error al guardar*\n\n"
                    "Hubo un problema al guardar los datos.\n"
                    "Por favor, intenta nuevamente."
                )
                
        except Exception as e:
            logger.error(f"Error al confirmar registro: {str(e)}")
            query.edit_message_text(
                "❌ *Error del sistema*\n\n"
                "Ocurrió un error inesperado. Contacta al administrador."
            )
    
    def cancel_registration(self, query, user_id):
        """Cancelar registro"""
        self.user_states.pop(user_id, None)
        self.client_data.pop(user_id, None)
        
        query.edit_message_text(
            "❌ *Registro cancelado*\n\n"
            "El registro ha sido cancelado.\n"
            "Usa /nuevo para comenzar un nuevo registro."
        )
    
    def resumen_diario(self, update: Update, context: CallbackContext):
        """Comando /resumen - mostrar resumen del día"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("❌ No tienes autorización para usar este bot.")
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
            
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error al obtener resumen: {str(e)}")
            update.message.reply_text("❌ Error al obtener el resumen diario.")
    
    def ver_habitaciones(self, update: Update, context: CallbackContext):
        """Comando /habitaciones - ver disponibilidad"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("❌ No tienes autorización para usar este bot.")
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
            
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error al obtener disponibilidad: {str(e)}")
            update.message.reply_text("❌ Error al obtener la disponibilidad.")
    
    def ayuda(self, update: Update, context: CallbackContext):
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
            "**Sobre las fotos de DNI:**\n"
            "• Funciona con fotos desde cualquier ángulo\n"
            "• El bot mejora automáticamente la calidad\n"
            "• Reconoce DNI peruanos, venezolanos y otros\n"
            "• Si una foto no funciona, intenta con otra\n\n"
            "**Soporte:**\n"
            "Si tienes problemas, contacta al administrador."
        )
        
        update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    def run(self):
        """Ejecutar el bot"""
        try:
            # Validar configuración
            Config.validate_config()
            
            # Crear updater
            updater = Updater(Config.TELEGRAM_BOT_TOKEN, use_context=True)
            dispatcher = updater.dispatcher
            
            # Agregar manejadores
            dispatcher.add_handler(CommandHandler("start", self.start))
            dispatcher.add_handler(CommandHandler("nuevo", self.nuevo_cliente))
            dispatcher.add_handler(CommandHandler("resumen", self.resumen_diario))
            dispatcher.add_handler(CommandHandler("habitaciones", self.ver_habitaciones))
            dispatcher.add_handler(CommandHandler("ayuda", self.ayuda))
            
            dispatcher.add_handler(MessageHandler(Filters.photo, self.handle_photo))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_text_input))
            dispatcher.add_handler(CallbackQueryHandler(self.handle_callback))
            
            # Iniciar bot
            logger.info("Bot iniciado exitosamente")
            updater.start_polling()
            updater.idle()
            
        except Exception as e:
            logger.error(f"Error al iniciar bot: {str(e)}")
            raise

if __name__ == "__main__":
    bot = HotelBot()
    bot.run() 