from services.whatsapp_service import send_message

async def handle_incoming_message(message: dict, contact: dict):
    """
    Procesa un mensaje entrante de WhatsApp
    """
    print("MENSAJE ENTRANTE:", message)
    print("CONTACTO:", contact)
    # if message.get("type") == "text":
    #     incoming_message = message.get("text", {}).get("body", "").lower().strip()
        
    #     if is_greeting(incoming_message):
    #         await send_welcome_message(to=message.get("from"), message_id=message.get("id"), sender_info=contact)
    if message.get("type") != "text":
        return

    message_id = message.get("id")
    #if not message_id or not message_id.startswith("wamid."):
    if not message_id:
        print("⚠️ Mensaje sin message_id, no se puede responder")
        return

    incoming_message = message.get("text", {}).get("body", "").lower().strip()

    if is_greeting(incoming_message):
        await send_welcome_message(
            to=message.get("from"),
            message_id=message_id,
            sender_info=contact
        )

def is_greeting(message: str) -> bool:
    """
    Detecta si el mensaje es un saludo
    """
    greetings = ["hola", "buenas tardes", "buenos días", "buenas noches"]
    #return message in greetings
    return any(greet in message for greet in greetings)


def get_sender_name(sender_info: dict) -> str:
    """
    Obtiene el nombre del remitente
    """
    return sender_info.get("profile", {}).get("name") or sender_info.get("wa_id", "Usuario")

async def send_welcome_message(to: str, message_id: str, sender_info: dict):
    """
    Envía un mensaje de bienvenida
    """
    print("ENVIANDO MENSAJE A:", to)
    name = get_sender_name(sender_info)
    welcome_message = f"Hola {name}, ¡Bienvenido a Los Motes de la Magdalena! 🎉 ¿En qué puedo ayudarte hoy?"
    await send_message(to, welcome_message, message_id)
