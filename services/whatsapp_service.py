from services.send_message_service import send_to_whatsapp

async def send_message(to: str, body: str, message_id: str):
    """
    Envía un mensaje a WhatsApp
    """
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": body},
    }
    
    await send_to_whatsapp(data)
