from turtle import mode
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv
from services.message_service import process_message
import os

load_dotenv()

WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

router = APIRouter()

@router.get("/webhook")
async def verify_Webhook(request: Request):
    """
    Verifica el webhook con WhatsApp.
    WhatsApp envía: hub.mode, hub.challenge, hub.verify_token
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid verify token")


@router.post("/webhook")
async def handle_incoming(request: Request):
    """
    Recibe mensajes de WhatsApp y los procesa
    """
    payload = await request.json()

    # Validar que es un mensaje de WhatsApp
    if payload.get("object") == "whatsapp_business_account":
        # Extrae mensaje y contacto
        message = payload.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [None])[0]
        contact = payload.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("contacts", [None])[0]

        if message:
            await process_message(message, contact)
    
    return {"status": "ok"}
