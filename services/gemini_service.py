# Fallback con Gemini API (opcional)
"""
Servicio de fallback usando Google Gemini para manejar
consultas que el modelo NLP local no puede resolver con confianza.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Importar Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai no instalado. Fallback de Gemini no disponible.")


# Configuración
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
CONFIDENCE_THRESHOLD = float(os.getenv("GEMINI_CONFIDENCE_THRESHOLD", "0.4"))

MENU_URL = "https://www.losmotesdelamagdalena.com/menu/"

# Prompt del sistema para el chatbot
SYSTEM_PROMPT = """Eres el asistente virtual de "Los Motes de la Magdalena", un restaurante tradicional ecuatoriano.

INFORMACIÓN DEL RESTAURANTE:
- Especialidad: Comida tradicional ecuatoriana (menudo, mote, hornado, fritada, caldos, etc.)
- Menú completo: {menu_url}
- Horario: Lunes a Domingo de 8:00 AM a 4:00 PM
- Métodos de pago: Efectivo, tarjeta, transferencia
- Delivery: Disponible en Quito (verificar cobertura por sector)

PRODUCTOS DESTACADOS:
- Menudo de la Magdalena (sopa especial de la casa)
- Mote de la Magdalena (plato insignia)
- Hornado / Hornado Completo
- Fritada Tradicional / Fritada Completa
- Caldos: de Gallina, de 31, de Pata
- Tortillas con Caucara, Fritada o Chorizo
- Combos: Ideal, Compartir, Dupla Personal, Tradición 1 y 2
- Bebidas: Limonada, Jugos, Magchicha, Gaseosas

EXTRAS DISPONIBLES:
- Ají, Ají de Maní, Agrio, Mapaguira
- Chorizo, Morcilla, Maduros Fritos
- ½ Aguacate, Porción de Arroz, Porción de Mote

TU PERSONALIDAD:
- Amable, cálido y servicial
- Usa emojis moderadamente (🍲 🛒 📍 ✅)
- Respuestas concisas pero completas
- Siempre ofrece el link del menú cuando pregunten por precios o productos
- Si no puedes ayudar con algo, sugiere llamar al restaurante

INSTRUCCIONES:
1. Saluda cordialmente si es el primer mensaje
2. Ayuda con pedidos y consultas del menú
3. Para precios, siempre refiere al menú: {menu_url}
4. Si piden algo que no entiendes, pide aclaración amablemente
5. Confirma los pedidos antes de procesarlos
6. Mantén el contexto de la conversación"""


class GeminiService:
    """Servicio para generar respuestas con Gemini API."""
    
    def __init__(self):
        self.enabled = False
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa la conexión con Gemini API."""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini SDK no disponible")
            return
        
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY no configurada. Fallback deshabilitado.")
            return
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=SYSTEM_PROMPT.format(menu_url=MENU_URL)
            )
            self.enabled = True
            logger.info(f"Gemini fallback inicializado con modelo: {GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Error inicializando Gemini: {e}")
            self.enabled = False
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,
        user_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Genera una respuesta usando Gemini.
        
        Args:
            user_message: Mensaje del usuario
            conversation_history: Historial de conversación (opcional)
            user_name: Nombre del usuario (opcional)
            
        Returns:
            Respuesta generada o None si falla
        """
        if not self.enabled or not self.model:
            logger.warning("Gemini no disponible para generar respuesta")
            return None
        
        try:
            # Construir contexto con historial si existe
            messages = []
            
            if conversation_history:
                for msg in conversation_history[-10:]:  # Últimos 10 mensajes
                    role = "user" if msg.get("role") == "user" else "model"
                    messages.append({"role": role, "parts": [msg.get("content", "")]})
            
            # Agregar mensaje actual
            prompt = user_message
            if user_name:
                prompt = f"[Usuario: {user_name}] {user_message}"
            
            messages.append({"role": "user", "parts": [prompt]})
            
            # Crear chat y obtener respuesta
            chat = self.model.start_chat(history=messages[:-1] if len(messages) > 1 else [])
            response = chat.send_message(prompt)
            
            if response and response.text:
                logger.info(f"Gemini generó respuesta de {len(response.text)} caracteres")
                return response.text.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {e}")
            return None
    
    def is_available(self) -> bool:
        """Verifica si Gemini está disponible."""
        return self.enabled and self.model is not None


# Instancia singleton
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Obtiene la instancia singleton del servicio Gemini."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


async def gemini_fallback(
    user_message: str,
    conversation_history: Optional[list] = None,
    user_name: Optional[str] = None
) -> Optional[str]:
    """
    Función de conveniencia para usar el fallback de Gemini.
    
    Args:
        user_message: Mensaje del usuario
        conversation_history: Historial opcional
        user_name: Nombre del usuario opcional
        
    Returns:
        Respuesta de Gemini o None
    """
    service = get_gemini_service()
    return await service.generate_response(user_message, conversation_history, user_name)
