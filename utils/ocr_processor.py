import re
import io
import base64
from openai import OpenAI
from PIL import Image, ImageEnhance, ImageFilter
import logging
from config import Config

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Procesador de OCR para extraer datos de DNI usando OpenAI Vision"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Modelo optimizado para vision
    
    def extract_text_from_image(self, image_bytes):
        """Extrae texto de una imagen usando OpenAI Vision API con múltiples intentos"""
        try:
            # Intento 1: Imagen original
            logger.info("Intentando extracción con imagen original...")
            result = self._try_extraction(image_bytes, "original")
            if result and self._is_extraction_successful(result):
                return result
            
            # Intento 2: Imagen mejorada (contraste y nitidez)
            logger.info("Intentando extracción con imagen mejorada...")
            enhanced_bytes = self._enhance_image(image_bytes)
            if enhanced_bytes:
                result = self._try_extraction(enhanced_bytes, "enhanced")
                if result and self._is_extraction_successful(result):
                    return result
            
            # Intento 3: Con prompt más específico para ángulos difíciles
            logger.info("Intentando extracción con prompt especializado para ángulos...")
            result = self._try_extraction_angle_specific(image_bytes)
            if result and self._is_extraction_successful(result):
                return result
            
            # Intento 4: Imagen reescalada y mejorada
            logger.info("Intentando extracción con imagen reescalada...")
            rescaled_bytes = self._rescale_image(image_bytes)
            if rescaled_bytes:
                result = self._try_extraction(rescaled_bytes, "rescaled")
                if result:
                    return result
            
            # Si todos los intentos fallan, devolver el mejor resultado
            logger.warning("Todos los intentos de extracción tuvieron resultados limitados")
            return result if result else ""
            
        except Exception as e:
            logger.error(f"Error al extraer texto con OpenAI: {str(e)}")
            return ""
    
    def _try_extraction(self, image_bytes, attempt_type="default"):
        """Intenta extraer texto con el prompt estándar"""
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analiza esta imagen de un DNI/cédula de identidad y extrae TODO el texto visible. 

IMPORTANTE:
- La imagen puede estar tomada desde un ángulo diferente
- Algunos textos pueden estar inclinados o distorsionados
- Identifica y extrae todos los números, nombres, fechas visible
- Mantén la estructura y saltos de línea tal como aparecen
- Si hay texto parcialmente visible, inclúyelo de todas formas
- Presta especial atención a:
  * Nombres y apellidos (pueden estar en múltiples líneas)  
  * Números de 8 dígitos (DNI/cédula)
  * Fechas de nacimiento
  * País/nacionalidad

Devuelve ÚNICAMENTE el texto extraído sin comentarios adicionales."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.05  # Temperatura muy baja para máxima precisión
            )
            
            extracted_text = response.choices[0].message.content.strip()
            logger.info(f"Texto extraído exitosamente ({attempt_type}): {len(extracted_text)} caracteres")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error en intento {attempt_type}: {str(e)}")
            return ""
    
    def _try_extraction_angle_specific(self, image_bytes):
        """Intenta extracción con prompt específico para imágenes con ángulos difíciles"""
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Esta imagen de DNI/cédula puede estar tomada desde un ángulo lateral o inclinado. 

ANÁLISIS ESPECIAL REQUERIDO:
- La perspectiva puede hacer que el texto se vea distorsionado
- Algunos campos pueden estar parcialmente ocultos o inclinados
- El texto puede aparecer más pequeño en algunas áreas debido al ángulo
- Enfócate especialmente en identificar:

1. NOMBRES COMPLETOS (puede estar dividido en varias líneas)
2. NÚMERO DE DOCUMENTO (8 dígitos para Perú, 7-8 para Venezuela)
3. FECHA DE NACIMIENTO (DD/MM/AAAA o DD MM AAAA)
4. NACIONALIDAD/PAÍS

INSTRUCCIONES:
- Lee cada parte de la imagen cuidadosamente
- Si el texto está borroso o inclinado, haz tu mejor interpretación
- Incluye TODO el texto que puedas distinguir
- No omitas información por estar parcialmente visible
- Organiza la información manteniendo la estructura del documento

Extrae TODO el texto visible:"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            extracted_text = response.choices[0].message.content.strip()
            logger.info(f"Texto extraído con prompt de ángulo: {len(extracted_text)} caracteres")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error en extracción específica para ángulos: {str(e)}")
            return ""
    
    def _enhance_image(self, image_bytes):
        """Mejora la imagen aumentando contraste y nitidez"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir a RGB si es necesario
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Aumentar contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)  # Aumentar contraste 30%
            
            # Aumentar nitidez
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)  # Aumentar nitidez 50%
            
            # Mejorar brillo ligeramente
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  # Aumentar brillo 10%
            
            # Aplicar filtro para reducir ruido
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            # Convertir de vuelta a bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95, optimize=True)
            enhanced_bytes = output.getvalue()
            
            logger.info(f"Imagen mejorada: {len(image_bytes)} -> {len(enhanced_bytes)} bytes")
            return enhanced_bytes
            
        except Exception as e:
            logger.error(f"Error al mejorar imagen: {str(e)}")
            return None
    
    def _rescale_image(self, image_bytes):
        """Reescala la imagen a un tamaño óptimo para OCR"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Obtener dimensiones actuales
            width, height = image.size
            
            # Definir tamaño objetivo optimizado para OCR (más grande que el anterior)
            target_width = 1800
            target_height = int(height * (target_width / width))
            
            # Solo reescalar si es diferente del tamaño actual
            if abs(width - target_width) > 100:  # Solo si hay diferencia significativa
                # Usar algoritmo de alta calidad para reescalar
                image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convertir a RGB si es necesario
                if image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
                
                # Guardar con alta calidad
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=95, optimize=True)
                rescaled_bytes = output.getvalue()
                
                logger.info(f"Imagen reescalada: {width}x{height} -> {target_width}x{target_height}")
                return rescaled_bytes
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error al reescalar imagen: {str(e)}")
            return None
    
    def _is_extraction_successful(self, extracted_text):
        """Evalúa si la extracción fue exitosa buscando patrones clave"""
        if not extracted_text or len(extracted_text) < 20:
            return False
        
        text_upper = extracted_text.upper()
        
        # Buscar indicadores de éxito
        success_indicators = 0
        
        # 1. Hay un número que parece DNI (8 dígitos)
        if re.search(r'\b\d{8}\b', extracted_text):
            success_indicators += 2
        
        # 2. Hay palabras que indican que es un documento de identidad
        identity_words = ['DNI', 'IDENTIDAD', 'DOCUMENTO', 'CEDULA', 'REPUBLICA', 'PERU', 'VENEZUELA']
        for word in identity_words:
            if word in text_upper:
                success_indicators += 1
                break
        
        # 3. Hay fechas
        if re.search(r'\d{1,2}[/\-\s]\d{1,2}[/\-\s]\d{4}', extracted_text):
            success_indicators += 1
        
        # 4. Hay nombres (palabras solo con letras)
        name_pattern = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{2,}\b', text_upper)
        if len(name_pattern) >= 2:
            success_indicators += 1
        
        # Considerar exitoso si tiene al menos 2 indicadores
        logger.info(f"Indicadores de éxito encontrados: {success_indicators}")
        return success_indicators >= 2

    def extract_dni_data(self, extracted_text):
        """Extrae datos específicos del DNI del texto extraído usando OpenAI para análisis estructurado"""
        if not extracted_text:
            return {
                'nombre': None,
                'dni': None,
                'fecha_nacimiento': None,
                'nacionalidad': None
            }
        
        try:
            # Almacenar el texto extraído para usar en validación
            self._last_extracted_text = extracted_text
            
            # Usar OpenAI para extraer datos estructurados con prompt mejorado
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un experto en extracción de datos de documentos de identidad latinoamericanos (DNI, Cédulas, Carnets). 

TIPOS DE DOCUMENTOS SOPORTADOS:
- PERÚ: DNI (8 dígitos exactos)
- VENEZUELA: Cédula (V-12345678 o E-12345678, 7-8 dígitos)
- COLOMBIA: Cédula de Ciudadanía (8-10 dígitos)  
- CHILE: Carnet de Identidad (12.345.678-9)
- Otros documentos latinoamericanos

INSTRUCCIONES MEJORADAS DE EXTRACCIÓN:

1. NÚMERO ID - Busca con MÁXIMA PRIORIDAD:
   - Para PERÚ: exactamente 8 dígitos consecutivos
   - Para VENEZUELA: 7-8 dígitos después de V- o E-
   - Para otros países: 7-10 dígitos
   - Ignora números de serie, fechas o códigos internos
   - Extrae solo los dígitos principales (sin prefijos ni separadores)

2. NOMBRES - Combina TODOS los componentes del nombre:
   - Busca campos: "Nombres", "Apellidos", "Primer Apellido", "Segundo Apellido"
   - También busca líneas que contengan solo letras (posibles nombres)
   - Si están separados, úne todos los componentes: "APELLIDOS NOMBRES"
   - Elimina títulos como "Sr.", "Sra.", etc.

3. FECHA NACIMIENTO - Formatos múltiples:
   - DD/MM/AAAA, DD-MM-AAAA, DD MM AAAA (espacios)
   - DDMMAAAA (sin separadores: 18021994)
   - Busca cerca de palabras: "nacimiento", "fecha", "born"
   - Convierte siempre a formato DD/MM/AAAA

4. NACIONALIDAD - Determina por contexto:
   - PERÚ/PERU → "PERUANA"
   - VENEZUELA → "VENEZOLANA"
   - COLOMBIA → "COLOMBIANA"  
   - CHILE → "CHILENA"
   - Si no identificas el país, extrae lo que encuentres

FORMATO DE RESPUESTA (ESTRICTO JSON):
{
  "nombre": "NOMBRE COMPLETO" o null,
  "dni": "12345678" o null,
  "fecha_nacimiento": "18/02/1994" o null,
  "nacionalidad": "PERUANA" o null
}

IMPORTANTE: 
- Si no encuentras un dato, usa null (no string vacío)
- Prioriza la extracción del DNI y nombre sobre otros campos
- Si el texto está borroso/inclinado, haz tu mejor interpretación
- NO inventes datos, solo extrae lo que realmente veas"""
                    },
                    {
                        "role": "user",
                        "content": f"Analiza este texto de documento de identidad y extrae los datos con máxima precisión:\n\n{extracted_text}"
                    }
                ],
                max_tokens=400,
                temperature=0.05  # Temperatura muy baja para máxima precisión
            )
            
            # Parsear respuesta JSON
            import json
            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Respuesta cruda de OpenAI: {raw_response}")
            
            # Limpiar la respuesta si tiene texto adicional
            if raw_response.startswith('```json'):
                raw_response = raw_response.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(raw_response)
            logger.info(f"JSON parseado: {result}")
            
            # Validar y limpiar datos extraídos
            cleaned_data = self._validate_and_clean_data(result)
            
            logger.info(f"Datos finales limpiados: {cleaned_data}")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error al estructurar datos con OpenAI: {str(e)}")
            # Fallback: usar método de regex tradicional mejorado
            fallback_data = self._extract_dni_data_regex_enhanced(extracted_text)
            logger.info(f"Fallback data: {fallback_data}")
            return fallback_data

    def _validate_and_clean_data(self, data):
        """Valida y limpia los datos extraídos"""
        cleaned = {
            'nombre': None,
            'dni': None,
            'fecha_nacimiento': None,
            'nacionalidad': None
        }
        
        # Validar nombre - más permisivo
        if data.get('nombre') and isinstance(data['nombre'], str) and data['nombre'] != 'null':
            nombre = data['nombre'].strip().upper()
            if len(nombre) > 2 and nombre not in ['NULL', 'N/A', 'NO ENCONTRADO', 'NO DETECTADO', 'NONE']:
                # Limpiar caracteres especiales del nombre
                nombre = re.sub(r'[^\w\s]', '', nombre)
                if len(nombre) > 3:
                    cleaned['nombre'] = nombre
        
        # Validar DNI/Cédula - más flexible para múltiples países
        if data.get('dni') and str(data['dni']) != 'null':
            dni_clean = re.sub(r'[^\d]', '', str(data['dni']))
            # Perú: 8 dígitos, Venezuela: 7-8 dígitos, Colombia: 8-10 dígitos
            if 7 <= len(dni_clean) <= 10 and dni_clean != '00000000':
                cleaned['dni'] = dni_clean
        
        # Usar métodos de emergencia para todos los datos faltantes
        if hasattr(self, '_last_extracted_text') and self._last_extracted_text:
            # DNI de emergencia
            if not cleaned['dni']:
                emergency_dni = self._emergency_dni_extraction(self._last_extracted_text)
                if emergency_dni:
                    cleaned['dni'] = emergency_dni
                    logger.info(f"DNI recuperado por método de emergencia: {emergency_dni}")
            
            # Nombre de emergencia
            if not cleaned['nombre']:
                emergency_name = self._emergency_name_extraction(self._last_extracted_text)
                if emergency_name:
                    cleaned['nombre'] = emergency_name
                    logger.info(f"Nombre recuperado por método de emergencia: {emergency_name}")
            
            # Fecha de emergencia
            if not cleaned['fecha_nacimiento']:
                emergency_date = self._emergency_date_extraction(self._last_extracted_text)
                if emergency_date:
                    cleaned['fecha_nacimiento'] = emergency_date
                    logger.info(f"Fecha recuperada por método de emergencia: {emergency_date}")
        
        # Validar fecha de nacimiento - más flexible
        if data.get('fecha_nacimiento') and str(data['fecha_nacimiento']) != 'null':
            fecha = str(data['fecha_nacimiento']).strip()
            if re.match(r'\d{1,2}[/\s-]\d{1,2}[/\s-]\d{4}', fecha):
                # Normalizar formato
                fecha = re.sub(r'[\s-]', '/', fecha)
                cleaned['fecha_nacimiento'] = fecha
            elif re.match(r'\d{2}\d{2}\d{4}', fecha) and len(fecha) == 8:
                # Formato sin separadores: 18021994 -> 18/02/1994
                cleaned['fecha_nacimiento'] = f"{fecha[:2]}/{fecha[2:4]}/{fecha[4:]}"
        
        # Validar nacionalidad
        if data.get('nacionalidad') and isinstance(data['nacionalidad'], str):
            nacionalidad = data['nacionalidad'].strip().upper()
            if len(nacionalidad) > 2 and not nacionalidad in ['NULL', 'N/A', 'NO ENCONTRADO']:
                cleaned['nacionalidad'] = nacionalidad
        
        return cleaned

    def _extract_dni_data_regex_enhanced(self, extracted_text):
        """Método de fallback mejorado usando regex para extraer datos del DNI"""
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
        
        # Extraer DNI mejorado - múltiples patrones más agresivos
        dni_patterns = [
            r'DNI\s*:?\s*(\d{8})',     # DNI: 12345678
            r'N[°º]?\s*(\d{8})',       # N° 12345678 o Nº 12345678
            r'(\d{8})\s*-?\s*\d',      # 12345678-9 (con dígito verificador)
            r'\b(\d{8})\b',            # 8 dígitos con bordes de palabra
            r'(\d{8})',                # Cualquier 8 dígitos consecutivos
            r'(\d{2}\s?\d{3}\s?\d{3})', # Con espacios: 12 345 678
        ]
        
        for pattern in dni_patterns:
            dni_matches = re.findall(pattern, text)
            for match in dni_matches:
                # Limpiar espacios y validar
                dni_candidate = re.sub(r'\s', '', match)
                if (len(dni_candidate) == 8 and 
                    dni_candidate.isdigit() and 
                    dni_candidate not in ['00000000', '12345678'] and
                    not dni_candidate.startswith('000')):
                    data['dni'] = dni_candidate
                    logger.info(f"DNI extraído por regex: {dni_candidate}")
                    break
            if data['dni']:
                break
        
        # Extraer fecha de nacimiento mejorado
        date_patterns = [
            r'FECHA\s+DE\s+NACIMIENTO\s+(\d{2})\s+(\d{2})\s+(\d{4})',
            r'NACIMIENTO\s+(\d{2})\s+(\d{2})\s+(\d{4})',
            r'(\d{2})\s+(\d{2})\s+(\d{4})',
            r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',
            r'(\d{2})(\d{2})(\d{4})',  # Sin separadores
        ]
        
        for pattern in date_patterns:
            date_matches = re.findall(pattern, text)
            for match in date_matches:
                if len(match) == 3:
                    day, month, year = match
                    if (1 <= int(day) <= 31 and 
                        1 <= int(month) <= 12 and 
                        1920 <= int(year) <= 2010):
                        data['fecha_nacimiento'] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                        logger.info(f"Fecha extraída por regex: {data['fecha_nacimiento']}")
                        break
            if data['fecha_nacimiento']:
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
        
        # Extraer nombres con método mejorado
        data['nombre'] = self._extract_name_from_text_enhanced(text, lines)
        
        return data
    
    def _extract_name_from_text_enhanced(self, text, lines):
        """Extrae el nombre completo del texto del DNI - método mejorado"""
        try:
            found_names = []
            
            # Método 1: Buscar campos específicos de nombres
            name_fields = ['APELLIDOS', 'NOMBRES', 'PRIMER APELLIDO', 'SEGUNDO APELLIDO', 'PRE NOMBRES']
            
            for line in lines:
                for field in name_fields:
                    if field in line:
                        # Extraer contenido después del campo
                        parts = line.split(field, 1)
                        if len(parts) > 1:
                            name_content = parts[1].strip()
                            # Limpiar caracteres especiales del inicio
                            name_content = re.sub(r'^[:\s\-]+', '', name_content)
                            if len(name_content) > 2 and re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', name_content):
                                found_names.append(name_content)
            
            # Método 2: Buscar líneas que parezcan nombres (solo si no encontró campos específicos)
            if not found_names:
                potential_names = []
                for line in lines:
                    # Línea que contiene solo letras, espacios y es suficientemente larga
                    if (re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', line) and 
                        len(line) > 4 and 
                        len(line.split()) >= 2 and  # Al menos 2 palabras
                        line not in ['REPUBLICA DEL PERU', 'DOCUMENTO NACIONAL', 'REGISTRO NACIONAL']):
                        
                        # Calcular "score" de probabilidad de ser nombre
                        score = 0
                        if len(line.split()) >= 3:  # Múltiples palabras
                            score += 2
                        if 5 <= len(line) <= 30:   # Longitud razonable
                            score += 1
                        if not any(word in line for word in ['IDENTIDAD', 'NACIONAL', 'REGISTRO']):
                            score += 1
                        
                        potential_names.append((line, score))
                
                # Ordenar por score y tomar el mejor
                if potential_names:
                    potential_names.sort(key=lambda x: x[1], reverse=True)
                    found_names.append(potential_names[0][0])
            
            # Construir nombre final
            if found_names:
                # Remover duplicados y combinar
                unique_parts = []
                for name in found_names:
                    words = name.split()
                    for word in words:
                        if word not in unique_parts:
                            unique_parts.append(word)
                
                full_name = ' '.join(unique_parts)
                if len(full_name) > 3:
                    logger.info(f"Nombre extraído (método mejorado): {full_name}")
                    return full_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error al extraer nombre mejorado: {str(e)}")
            return None
    
    def resize_image_if_needed(self, image_bytes, max_size=20 * 1024 * 1024):
        """Redimensiona la imagen si es muy grande para OpenAI Vision API (límite 20MB)"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # OpenAI Vision tiene límite de 20MB, pero es mejor optimizar
            if len(image_bytes) > max_size:
                # Calcular nuevo tamaño manteniendo aspecto (OpenAI recomienda máximo 2048x2048)
                width, height = image.size
                max_dimension = 2048
                
                if width > max_dimension or height > max_dimension:
                    ratio = min(max_dimension/width, max_dimension/height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    
                    # Redimensionar
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir de vuelta a bytes con calidad optimizada
                output = io.BytesIO()
                
                # Convertir a RGB si es necesario (para JPEG)
                if image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
                
                image.save(output, format='JPEG', quality=90, optimize=True)
                optimized_bytes = output.getvalue()
                
                logger.info(f"Imagen redimensionada: {len(image_bytes)} -> {len(optimized_bytes)} bytes")
                return optimized_bytes
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error al redimensionar imagen: {str(e)}")
            return image_bytes
    
    def analyze_dni_quality(self, image_bytes):
        """Analiza la calidad de la imagen del DNI usando OpenAI"""
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analiza la calidad de esta imagen de DNI/cédula y responde únicamente con un JSON:
                                {
                                  "quality_score": 1-10,
                                  "is_readable": true/false,
                                  "issues": ["problema1", "problema2"],
                                  "suggestions": ["mejora1", "mejora2"]
                                }
                                
                                Evalúa: nitidez, iluminación, ángulo, legibilidad del texto."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            import json
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"Error al analizar calidad de imagen: {str(e)}")
            return {
                "quality_score": 5,
                "is_readable": True,
                "issues": [],
                "suggestions": []
            }
    
    def _emergency_dni_extraction(self, text):
        """Método de emergencia para extraer DNI usando múltiples patrones agresivos"""
        try:
            # Patrones para múltiples países
            emergency_patterns = [
                # Patrones peruanos
                r'\b(\d{8})\b',           # 8 dígitos con bordes de palabra
                r'(\d{8})',               # Cualquier 8 dígitos
                r'N°?\s*(\d{8})',         # Con N° antes
                
                # Patrones venezolanos  
                r'V\s*(\d{2}\.\d{3}\.\d{3})',  # V 20.759.196
                r'V\s*(\d{8})',              # V 20759196
                r'V[\s\-]*(\d{2}[\.\s]*\d{3}[\.\s]*\d{3})',  # Variaciones V-
                r'E\s*(\d{2}\.\d{3}\.\d{3})',  # E 20.759.196
                r'E\s*(\d{8})',              # E 20759196
                
                # Patrones generales
                r'(\d{2}\.\d{3}\.\d{3})',    # 20.759.196 (venezolano)
                r'(\d{2}[\s\-]\d{3}[\s\-]\d{3})', # Con espacios o guiones
                r'(\d{7,10})',               # 7-10 dígitos (colombianos, otros)
            ]
            
            for pattern in emergency_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Limpiar el match
                    dni_candidate = re.sub(r'[^\d]', '', match)
                    
                    # Validar que sea exactamente 8 dígitos y no sea obvio que no es DNI
                    if (len(dni_candidate) == 8 and 
                        dni_candidate.isdigit() and 
                        dni_candidate != '00000000' and 
                        not dni_candidate.startswith('000') and
                        not dni_candidate == '12345678' and  # DNI de ejemplo
                        not all(c == dni_candidate[0] for c in dni_candidate)):  # No todos iguales
                        
                        logger.info(f"DNI encontrado por método de emergencia: {dni_candidate}")
                        return dni_candidate
            
            return None
            
        except Exception as e:
            logger.error(f"Error en extracción de emergencia: {str(e)}")
            return None
    
    def _emergency_name_extraction(self, text):
        """Método de emergencia para extraer nombres - genérico para múltiples países"""
        try:
            found_parts = []
            lines = text.upper().split('\n')
            
            # Patrones para diferentes países
            name_fields = ['APELLIDOS', 'NOMBRES', 'PRIMER APELLIDO', 'SEGUNDO APELLIDO']
            
            # Buscar líneas con campos de nombres
            for line in lines:
                line = line.strip()
                
                # Buscar líneas que empiecen con campos de nombre
                for field in name_fields:
                    if line.startswith(field):
                        # Extraer el contenido después del campo
                        parts = line.split(maxsplit=1)
                        if len(parts) > 1:
                            name_content = parts[1].strip()
                            if len(name_content) > 2 and re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', name_content):
                                found_parts.append(name_content)
            
            # Si no encontró campos específicos, buscar patrones de nombres
            if not found_parts:
                for line in lines:
                    line = line.strip()
                    # Buscar líneas que contengan solo letras y espacios
                    if (re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', line) and 
                        len(line.split()) >= 2 and 
                        len(line) > 5 and
                        line not in ['REPUBLICA BOLIVARIANA DE VENEZUELA', 'CEDULA DE IDENTIDAD', 'DOCUMENTO NACIONAL', 'REGISTRO NACIONAL']):
                        found_parts.append(line)
            
            # Construir nombre completo
            if found_parts:
                full_name = ' '.join(found_parts).strip()
                # Limpiar duplicados de palabras
                words = full_name.split()
                unique_words = []
                for word in words:
                    if word not in unique_words:
                        unique_words.append(word)
                
                full_name = ' '.join(unique_words)
                if len(full_name) > 5:
                    logger.info(f"Nombre reconstruido: {full_name}")
                    return full_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error en extracción de emergencia de nombre: {str(e)}")
            return None
    
    def _emergency_date_extraction(self, text):
        """Método de emergencia para extraer fecha de nacimiento"""
        try:
            # Patrones para fechas
            date_patterns = [
                r'(\d{2})\s+(\d{2})\s+(\d{4})',  # 18 02 1994
                r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',  # 18/02/1994 o 18-02-1994
                r'Fecha de Nacimiento\s+(\d{2})\s+(\d{2})\s+(\d{4})',
                r'(\d{2})(\d{2})(\d{4})',  # 18021994
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if len(match) == 3:  # día, mes, año
                        day, month, year = match
                        
                        # Validar fecha lógica
                        if (1 <= int(day) <= 31 and 
                            1 <= int(month) <= 12 and 
                            1900 <= int(year) <= 2010):  # Rango razonable para DNI
                            
                            formatted_date = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                            logger.info(f"Fecha encontrada: {formatted_date}")
                            return formatted_date
            
            return None
            
        except Exception as e:
            logger.error(f"Error en extracción de emergencia de fecha: {str(e)}")
            return None 