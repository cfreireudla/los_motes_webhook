from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE")
API_VERSION = os.getenv("API_VERSION")
BASE_URL = os.getenv("BASE_URL")

async def send_to_whatsapp(data: dict):
    """
    Realiza la llamada a la API de WhatsApp
    """
    url = f"{BASE_URL}/{API_VERSION}/{BUSINESS_PHONE}/messages"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Error al enviar mensaje: {error}")
        return None
