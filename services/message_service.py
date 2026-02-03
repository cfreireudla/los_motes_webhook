from services.whatsapp_service import send_message

async def handle_incoming_message(message: dict, contact: dict):
    """
    Procesa un mensaje entrante de WhatsApp
    """
    if message.get("type") == "text":
        incoming_message = message.get("text", {}).get("body", "").lower().strip()
        
        if is_greeting(incoming_message):
            await send_welcome_message(message.get("from"), message.get("id"), contact)

def is_greeting(message: str) -> bool:
    """
    Detecta si el mensaje es un saludo
    """
    greetings = ["hola", "buenas tardes", "buenos días", "buenas noches"]
    return message in greetings

def get_sender_name(sender_info: dict) -> str:
    """
    Obtiene el nombre del remitente
    """
    return sender_info.get("profile", {}).get("name") or sender_info.get("wa_id", "Usuario")

async def send_welcome_message(to: str, message_id: str, sender_info: dict):
    """
    Envía un mensaje de bienvenida
    """
    name = get_sender_name(sender_info)
    welcome_message = f"Hola {name}, ¡Bienvenido a Los Motes de la Magdalena! 🎉 ¿En qué puedo ayudarte hoy?"
    await send_message(to, welcome_message, message_id)
