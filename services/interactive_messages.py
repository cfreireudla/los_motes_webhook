from services.send_message_service import send_to_whatsapp

async def send_text_message(to: str, body: str):
    """
    Envía un mensaje de texto simple
    """
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body}
    }
    return await send_to_whatsapp(data)

async def send_button_message(to: str, body: str, buttons: list):
    """
    Envía un mensaje con botones interactivos (máximo 3 botones)
    
    Ejemplo:
    buttons = [
        {"id": "menu", "title": "Ver Menú"},
        {"id": "help", "title": "Ayuda"}
    ]
    """
    if len(buttons) > 3:
        raise ValueError("WhatsApp solo permite máximo 3 botones")
    
    buttons_data = [
        {
            "type": "reply",
            "reply": {"id": btn["id"], "title": btn["title"]}
        }
        for btn in buttons
    ]
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": buttons_data}
        }
    }
    return await send_to_whatsapp(data)

async def send_list_message(to: str, body: str, button_text: str, sections: list):
    """
    Envía un mensaje con lista interactiva
    
    Ejemplo:
    sections = [
        {
            "title": "Platos",
            "rows": [
                {"id": "prod_1", "title": "Hornado", "description": "$15"},
                {"id": "prod_2", "title": "Fritada", "description": "$14"}
            ]
        }
    ]
    """
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }
    return await send_to_whatsapp(data)
