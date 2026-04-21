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
from services.user_state_service import (
    get_or_create_user, 
    update_user_state,
    clear_user_cart,
    save_pending_order,
    get_pending_order,
    confirm_pending_order,
    clear_pending_order
)
from services.order_parser import parsear_pedido, ParseResult
from services.gemini_service import gemini_fallback, get_gemini_service, CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)

MENU_URL = "https://www.losmotesdelamagdalena.com/menu/"


class AIService:
    """
    Servicio de IA para procesar mensajes de texto libre.
    
    Clasifica la intención del usuario y ejecuta la acción correspondiente,
    o envía una respuesta de texto si no hay acción asociada.
    """
    
    def __init__(self):
        self.classifier = get_classifier()

    PAYMENT_METHODS = {"efectivo", "transferencia", "tarjeta", "de una", "deuna"}
    
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
        # Verificar si el usuario está esperando confirmación
        user = get_or_create_user(db, phone_number)
        text_lower = text.strip().lower()

        # Si el usuario ya está compartiendo dirección, cerrar flujo con confirmación humana
        if user.current_state == "AWAITING_LOCATION":
            update_user_state(db, phone_number, "INITIAL")
            await send_text_message(
                phone_number,
                "¡Gracias! ✅ Un asesor se va a comunicar contigo inmediatamente para coordinar la entrega."
            )
            return IntentResult(
                intent="compartir_ubicacion",
                confidence=1.0,
                response="",
                action=None,
                is_fallback=False
            )

        # Si el usuario escribe solo un método de pago, avanzar a pedir dirección
        if text_lower in self.PAYMENT_METHODS:
            update_user_state(db, phone_number, "AWAITING_LOCATION")
            await send_text_message(
                phone_number,
                "Perfecto, registré tu método de pago. 📍 Ayúdame con tu dirección para la entrega de pedido."
            )
            return IntentResult(
                intent="metodos_pago",
                confidence=1.0,
                response="",
                action="request_location",
                is_fallback=False
            )
        
        if user.current_state == "AWAITING_CONFIRMATION":
            # Usuario está confirmando un pedido pendiente
            if text_lower in ["sí", "si", "sip", "ok", "dale", "confirmo", "correcto", "esta bien", "está bien", "perfecto"]:
                await self._handle_confirmacion_pedido(phone_number, db)
                # Retornar un resultado dummy
                return IntentResult(
                    intent="confirmar_pedido",
                    confidence=1.0,
                    response="",
                    action=None,
                    is_fallback=False
                )
            elif text_lower in ["no", "cancelar", "cambiar", "modificar"]:
                clear_pending_order(db, phone_number)
                await send_text_message(
                    phone_number,
                    "❌ Pedido cancelado.\n\n📋 Menú: https://www.losmotesdelamagdalena.com/menu/\n\n✍️ Escríbeme tu pedido nuevamente cuando estes listo."
                )
                return IntentResult(
                    intent="cancelar_pedido",
                    confidence=1.0,
                    response="",
                    action=None,
                    is_fallback=False
                )
        
        # Clasificar el mensaje normalmente
        result = self.classifier.classify(text)
        
        logger.info(
            f"AI: '{text[:30]}...' -> {result.intent} "
            f"({result.confidence:.1%}) {'[fallback]' if result.is_fallback else ''}"
        )
        
        # Si es intent de pedido, usar el parser para extraer productos
        if result.intent == "realizar_pedido":
            parse_result = parsear_pedido(text)
            
            if parse_result.tiene_productos:
                # Hay productos detectados - mostrar confirmación
                await self._handle_pedido_con_productos(
                    phone_number=phone_number,
                    db=db,
                    parse_result=parse_result
                )
                return result
        
        # FALLBACK CON GEMINI: Si baja confianza y es fallback
        if result.is_fallback and result.confidence < CONFIDENCE_THRESHOLD:
            gemini_response = await self._try_gemini_fallback(
                text=text,
                sender_name=sender_name
            )
            if gemini_response:
                logger.info(f"AI: Usando respuesta de Gemini (confianza spaCy: {result.confidence:.1%})")
                await send_text_message(phone_number, gemini_response)
                return result
        
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
    
    async def _try_gemini_fallback(
        self,
        text: str,
        sender_name: str = "Usuario"
    ) -> Optional[str]:
        """
        Intenta obtener respuesta de Gemini como fallback.
        
        Args:
            text: Mensaje del usuario
            sender_name: Nombre del usuario
            
        Returns:
            Respuesta de Gemini o None si no disponible
        """
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            logger.debug("Gemini no disponible para fallback")
            return None
        
        try:
            response = await gemini_fallback(
                user_message=text,
                user_name=sender_name
            )
            return response
        except Exception as e:
            logger.error(f"Error en fallback de Gemini: {e}")
            return None
    
    async def _handle_pedido_con_productos(
        self,
        phone_number: str,
        db: Session,
        parse_result: ParseResult
    ):
        """
        Maneja un pedido cuando se detectaron productos.
        Guarda el pedido pendiente y muestra confirmación.
        """
        # Guardar el pedido parseado como pendiente
        order_data = {
            "productos": parse_result.productos,
            "extras": parse_result.extras,
            "sin_ingredientes": parse_result.sin_ingredientes,
            "con_ingredientes": parse_result.con_ingredientes,
            "mensaje_original": parse_result.mensaje_original
        }
        save_pending_order(db, phone_number, order_data)
        
        # Generar texto de confirmación
        confirmacion = parse_result.to_confirmation_text()
        
        # Construir mensaje completo
        mensaje = f"¡Perfecto! 🛒 Esto es lo que entendí:\n\n{confirmacion}"
        mensaje += "\n\n¿Es correcto? ✍️ Escríbeme *SÍ* para confirmar o indícame qué cambiar."
        
        # Log para debug
        productos_str = ", ".join(
            f"{p['cantidad']}x {p['producto_oficial']}" 
            for p in parse_result.productos
        )
        logger.info(f"Parser: Productos detectados: {productos_str}")
        
        await send_text_message(phone_number, mensaje)
    
    async def _handle_confirmacion_pedido(
        self,
        phone_number: str,
        db: Session
    ):
        """
        Maneja la confirmación del pedido.
        Guarda el pedido como confirmado y muestra mensaje final.
        """
        # Confirmar el pedido pendiente
        order_data = confirm_pending_order(db, phone_number)
        
        if not order_data:
            await send_text_message(
                phone_number,
                "No encontré un pedido pendiente. ✍️ Escríbeme tu pedido nuevamente."
            )
            return
        
        # Generar resumen del pedido confirmado
        productos = order_data.get("productos", [])
        resumen_lines = []
        for p in productos:
            resumen_lines.append(f"• {p['cantidad']}x {p['producto_oficial']}")
        resumen = "\n".join(resumen_lines)
        
        # Limpiar el pedido pendiente (ya está confirmado)
        clear_pending_order(db, phone_number)
        
        # Mensaje final de confirmación
        mensaje = f"✅ *¡Pedido confirmado!*\n\n"
        mensaje += f"📝 *Tu pedido:*\n{resumen}\n\n"
        mensaje += "🚀 Gracias por tu compra. En breve nos comunicaremos contigo para coordinar la entrega.\n\n"
        mensaje += "📞 Si tienes alguna pregunta, escríbenos."
        
        logger.info(f"Pedido confirmado para {phone_number}: {len(productos)} productos")
        
        await send_text_message(phone_number, mensaje)
    
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
        
        if action == "send_menu_link":
            # Enviar respuesta con link del menú (flujo simplificado)
            await send_text_message(phone_number, result.response)
        
        elif action == "show_menu_button":
            # Legacy: ahora solo envía texto con link
            await send_text_message(phone_number, result.response)
        
        elif action == "show_categories":
            # Legacy: ahora solo envía texto con link
            await send_text_message(phone_number, result.response)
        
        elif action == "start_order_flow":
            # Simplificado: solo envía mensaje, usuario escribe pedido
            await send_text_message(phone_number, result.response)
        
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
            cancel_msg = result.response + "\n\n📋 Menú: https://www.losmotesdelamagdalena.com/menu/\n✍️ Escríbeme cuando quieras hacer un nuevo pedido."
            await send_text_message(phone_number, cancel_msg)
        
        elif action == "request_human":
            # Solicitar atención humana
            await send_text_message(phone_number, result.response)
            # Aquí podrías agregar lógica para notificar a un humano
            logger.info(f"⚠️ Usuario {phone_number} solicita atención humana")

        elif action == "request_location":
            # Solicitar dirección de entrega y esperar ubicación
            update_user_state(db, phone_number, "AWAITING_LOCATION")
            await send_text_message(phone_number, result.response)
            logger.info(f"📍 Usuario {phone_number} en estado AWAITING_LOCATION")
        
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