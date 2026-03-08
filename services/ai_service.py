# Orquestador principal de IA
"""
Servicio de IA que orquesta la clasificación de intenciones
y ejecuta las acciones correspondientes.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from services.intent_classifier import get_classifier, IntentResult
from services.interactive_messages import send_text_message, send_button_message
from services.menu_service import send_main_menu, send_welcome_message
from services.user_state_service import get_or_create_user, clear_user_cart

logger = logging.getLogger(__name__)


class AIService:
    """
    Servicio de IA para procesar mensajes de texto libre.
    
    Clasifica la intención del usuario y ejecuta la acción correspondiente,
    o envía una respuesta de texto si no hay acción asociada.
    """
    
    def __init__(self):
        self.classifier = get_classifier()
    
    async def process_text_message(
        self,
        phone_number: str,
        text: str,
        db: Session,
        sender_name: str = "Usuario"
    ) -> IntentResult:
        """
        Procesa un mensaje de texto y ejecuta la acción correspondiente.
        
        Args:
            phone_number: Número de WhatsApp del usuario
            text: Texto del mensaje
            db: Sesión de base de datos
            sender_name: Nombre del usuario
            
        Returns:
            IntentResult con los detalles de la clasificación
        """
        # Clasificar el mensaje
        result = self.classifier.classify(text)
        
        logger.info(
            f"AI: '{text[:30]}...' -> {result.intent} "
            f"({result.confidence:.1%}) {'[fallback]' if result.is_fallback else ''}"
        )
        
        # Ejecutar acción si existe
        if result.action:
            await self._execute_action(
                action=result.action,
                phone_number=phone_number,
                db=db,
                sender_name=sender_name,
                result=result
            )
        else:
            # Solo enviar respuesta de texto
            await send_text_message(phone_number, result.response)
        
        return result
    
    async def _execute_action(
        self,
        action: str,
        phone_number: str,
        db: Session,
        sender_name: str,
        result: IntentResult
    ):
        """
        Ejecuta una acción específica basada en el intent detectado.
        
        Args:
            action: Nombre de la acción a ejecutar
            phone_number: Número de WhatsApp
            db: Sesión de base de datos
            sender_name: Nombre del usuario
            result: Resultado de la clasificación
        """
        logger.debug(f"Ejecutando acción: {action}")
        
        if action == "show_menu_button":
            # Enviar respuesta con botón para ver menú
            await send_button_message(
                to=phone_number,
                body=result.response,
                buttons=[
                    {"id": "show_menu", "title": "Ver Menú 📋"}
                ]
            )
        
        elif action == "show_categories":
            # Primero enviar respuesta, luego mostrar categorías
            await send_text_message(phone_number, result.response)
            await send_main_menu(phone_number, db)
        
        elif action == "start_order_flow":
            # Iniciar flujo de pedido
            await send_welcome_message(phone_number, sender_name, db)
        
        elif action == "show_current_order":
            # Mostrar carrito actual
            from services.menu_service import show_cart_and_confirm
            await send_text_message(phone_number, result.response)
            await show_cart_and_confirm(phone_number, db)
        
        elif action == "show_order_summary":
            # Mostrar resumen del pedido
            from services.menu_service import show_cart_and_confirm
            await show_cart_and_confirm(phone_number, db)
        
        elif action == "cancel_order":
            # Cancelar pedido
            user = get_or_create_user(db, phone_number)
            clear_user_cart(db, user.id)
            await send_button_message(
                to=phone_number,
                body=result.response,
                buttons=[
                    {"id": "show_menu", "title": "Nuevo Pedido 🛒"}
                ]
            )
        
        elif action == "request_human":
            # Solicitar atención humana
            await send_text_message(phone_number, result.response)
            # Aquí podrías agregar lógica para notificar a un humano
            logger.info(f"⚠️ Usuario {phone_number} solicita atención humana")
        
        else:
            # Acción desconocida, solo enviar respuesta
            logger.warning(f"Acción desconocida: {action}")
            await send_text_message(phone_number, result.response)
    
    def is_ready(self) -> bool:
        """Indica si el servicio está listo para procesar mensajes."""
        return self.classifier.is_loaded


# Instancia global del servicio
_ai_service_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """
    Obtiene la instancia global del servicio de IA.
    
    Returns:
        Instancia del AIService
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance


async def process_with_ai(
    phone_number: str,
    text: str,
    db: Session,
    sender_name: str = "Usuario"
) -> IntentResult:
    """
    Función de conveniencia para procesar un mensaje con IA.
    
    Args:
        phone_number: Número de WhatsApp del usuario
        text: Texto del mensaje
        db: Sesión de base de datos
        sender_name: Nombre del usuario
        
    Returns:
        IntentResult con los detalles de la clasificación
    """
    service = get_ai_service()
    return await service.process_text_message(phone_number, text, db, sender_name)