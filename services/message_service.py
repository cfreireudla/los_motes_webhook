from database.database import SessionLocal
from services.menu_service import (
    send_welcome_message,
    send_main_menu,
    send_category_products,
    add_product_to_cart,
    show_cart_and_confirm,
    confirm_order
)
from services.user_state_service import get_or_create_user, clear_user_cart
from services.user_state_service import update_user_state
from services.interactive_messages import send_text_message
from services.ai_service import process_with_ai, get_ai_service

async def process_message(message: dict, contact: dict):
    """
    Procesa un mensaje entrante de WhatsApp (nuevo flujo con estados)
    """
    db = SessionLocal()
    
    try:
        phone_number = message.get("from")
        message_type = message.get("type")
        
        print(f"📱 Mensaje de {phone_number} - Tipo: {message_type}")
        
        # Obtener o crear usuario
        user = get_or_create_user(db, phone_number)
        sender_name = get_sender_name(contact)
        
        # Manejar mensajes de texto con IA
        if message_type == "text":
            text_body = message.get("text", {}).get("body", "").strip()
            
            # Verificar si el clasificador está listo
            ai_service = get_ai_service()
            if ai_service.is_ready():
                # Procesar con IA
                result = await process_with_ai(
                    phone_number=phone_number,
                    text=text_body,
                    db=db,
                    sender_name=sender_name
                )
                print(f"🤖 IA: {result.intent} ({result.confidence:.1%})")
            else:
                # Fallback si el modelo no está cargado
                if is_greeting(text_body.lower()):
                    await send_welcome_message(phone_number, sender_name, db)
                else:
                    await send_text_message(
                        phone_number,
                        "Por favor, utiliza los botones del menú para realizar tu pedido. Escribe 'hola' para comenzar."
                    )
        
        # Manejar respuestas a botones
        elif message_type == "interactive":
            interactive_data = message.get("interactive", {})
            response_type = interactive_data.get("type")
            
            if response_type == "button_reply":
                button_id = interactive_data.get("button_reply", {}).get("id")
                await handle_button_response(phone_number, button_id, db)
            
            elif response_type == "list_reply":
                list_id = interactive_data.get("list_reply", {}).get("id")
                await handle_list_response(phone_number, list_id, db)

        # Manejar ubicación compartida desde WhatsApp
        elif message_type == "location":
            user = get_or_create_user(db, phone_number)
            if user.current_state == "AWAITING_LOCATION":
                update_user_state(db, phone_number, "INITIAL")
                await send_text_message(
                    phone_number,
                    "¡Gracias! ✅ Un asesor se va a comunicar contigo inmediatamente para coordinar la entrega."
                )
            else:
                await send_text_message(
                    phone_number,
                    "¡Ubicación recibida! 📍 Si deseas, también puedes escribirnos tu dirección para continuar con el pedido."
                )
        
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

async def handle_button_response(phone_number: str, button_id: str, db):
    """
    Maneja las respuestas de botones interactivos
    """
    if button_id == "show_menu":
        await send_main_menu(phone_number, db)
    
    elif button_id == "continue_shopping":
        await send_main_menu(phone_number, db)
    
    elif button_id == "view_cart":
        await show_cart_and_confirm(phone_number, db)
    
    elif button_id == "confirm_order":
        await show_cart_and_confirm(phone_number, db)
    
    elif button_id == "confirm_final":
        await confirm_order(phone_number, db)
    
    elif button_id == "cancel_order":
        clear_user_cart(db, get_or_create_user(db, phone_number).id)
        await send_text_message(phone_number, "❌ Pedido cancelado. Escribe 'hola' para volver a empezar.")

async def handle_list_response(phone_number: str, list_id: str, db):
    """
    Maneja las respuestas de listas interactivas
    """
    # Paginación de productos en categoría (debe estar antes de cat_)
    if "_page_" in list_id and list_id.startswith("cat_"):
        # Formato: cat_{category_id}_page_{page}
        parts = list_id.split("_")
        category_id = int(parts[1])
        page = int(parts[3])
        await send_category_products(phone_number, category_id, db, page)
    
    # Respuestas de categorías
    elif list_id.startswith("cat_"):
        category_id = int(list_id.replace("cat_", ""))
        await send_category_products(phone_number, category_id, db)
    
    # Paginacion del menu principal
    elif list_id.startswith("menu_page_"):
        page = int(list_id.replace("menu_page_", ""))
        await send_main_menu(phone_number, db, page)
    
    # Respuestas de productos
    elif list_id.startswith("prod_"):
        product_id = int(list_id.replace("prod_", ""))
        await add_product_to_cart(phone_number, product_id, db)
    
    # Volver al menú
    elif list_id == "back_to_menu":
        await send_main_menu(phone_number, db)

def is_greeting(text: str) -> bool:
    """
    Detecta si el mensaje es un saludo
    """
    greetings = ["hola", "hello", "hi", "buenas tardes", "buenos días", "buenas noches", "hey"]
    return any(greet in text for greet in greetings)

def get_sender_name(contact: dict) -> str:
    """
    Obtiene el nombre del remitente
    """
    if not contact:
        return "Usuario"
    return contact.get("profile", {}).get("name") or contact.get("wa_id", "Usuario")
