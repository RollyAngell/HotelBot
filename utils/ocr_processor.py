import re
import io
from google.cloud import vision
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Procesador de OCR para extraer datos de DNI"""
    
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    def extract_text_from_image(self, image_bytes):
        """Extrae texto de una imagen usando Google Cloud Vision API"""
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f'Error en OCR: {response.error.message}')
            
            texts = response.text_annotations
            if texts:
                return texts[0].description
            else:
                return ""
        except Exception as e:
            logger.error(f"Error al extraer texto de la imagen: {str(e)}")
            return ""
    
    def extract_dni_data(self, extracted_text):
        """Extrae datos específicos del DNI del texto extraído"""
        data = {
            'nombre': None,
            'dni': None,
            'fecha_nacimiento': None,
            'nacionalidad': None
        }
        
        if not extracted_text:
            return data
        
        # Limpiar texto
        text = extracted_text.upper().strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extraer DNI (8 dígitos)
        dni_pattern = r'\b\d{8}\b'
        dni_match = re.search(dni_pattern, text)
        if dni_match:
            data['dni'] = dni_match.group()
        
        # Extraer fecha de nacimiento (varios formatos)
        date_patterns = [
            r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',
            r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b',
            r'\b(\d{4})/(\d{1,2})/(\d{1,2})\b'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                data['fecha_nacimiento'] = date_match.group()
                break
        
        # Extraer nacionalidad
        if 'PERU' in text or 'PERUANA' in text or 'PERUANO' in text:
            data['nacionalidad'] = 'PERUANA'
        elif 'VENEZOLANA' in text or 'VENEZUELA' in text:
            data['nacionalidad'] = 'VENEZOLANA'
        elif 'COLOMBIANA' in text or 'COLOMBIA' in text:
            data['nacionalidad'] = 'COLOMBIANA'
        elif 'ECUATORIANA' in text or 'ECUADOR' in text:
            data['nacionalidad'] = 'ECUATORIANA'
        
        # Extraer nombres (lógica más compleja)
        data['nombre'] = self._extract_name_from_text(text, lines)
        
        return data
    
    def _extract_name_from_text(self, text, lines):
        """Extrae el nombre completo del texto del DNI"""
        try:
            # Buscar líneas que contengan nombres
            name_keywords = ['NOMBRES', 'APELLIDOS', 'PRIMER NOMBRE', 'SEGUNDO NOMBRE']
            name_lines = []
            
            for i, line in enumerate(lines):
                # Si la línea contiene keywords de nombres
                if any(keyword in line for keyword in name_keywords):
                    # Extraer el nombre de la misma línea o la siguiente
                    if ':' in line:
                        name_part = line.split(':', 1)[1].strip()
                        if name_part and len(name_part) > 2:
                            name_lines.append(name_part)
                    elif i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and len(next_line) > 2:
                            name_lines.append(next_line)
            
            if name_lines:
                # Combinar nombres encontrados
                full_name = ' '.join(name_lines).strip()
                # Limpiar caracteres especiales
                full_name = re.sub(r'[^A-ZÁÉÍÓÚÑ\s]', '', full_name)
                return full_name if len(full_name) > 3 else None
            
            # Si no se encontraron keywords, buscar líneas que parezcan nombres
            for line in lines:
                # Buscar líneas que contengan solo letras y espacios
                if re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', line) and len(line) > 5:
                    # Evitar líneas que contengan palabras comunes del DNI
                    dni_words = ['DOCUMENTO', 'IDENTIDAD', 'REPUBLICA', 'PERU', 'NACIONAL']
                    if not any(word in line for word in dni_words):
                        return line.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error al extraer nombre: {str(e)}")
            return None
    
    def resize_image_if_needed(self, image_bytes, max_size=4 * 1024 * 1024):
        """Redimensiona la imagen si es muy grande para el OCR"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Si la imagen es muy grande, redimensionarla
            if len(image_bytes) > max_size:
                # Calcular nuevo tamaño manteniendo aspecto
                width, height = image.size
                ratio = min(1920/width, 1080/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # Redimensionar
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir de vuelta a bytes
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=85)
                return output.getvalue()
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error al redimensionar imagen: {str(e)}")
            return image_bytes 