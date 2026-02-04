from dotenv import load_dotenv
import os
import httpx

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
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(url, json=data, headers=headers)
    #         response.raise_for_status()
    #         return response.json()
    # except httpx.RequestError as error:
    #     print(f"Error al enviar mensaje: {error}")
    #     return None
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

        print("ENVIANDO A WHATSAPP:", data)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()
        return response.json()
