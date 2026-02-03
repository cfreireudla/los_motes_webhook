from fastapi import APIRouter

router = APIRouter()

@router.post("/webhook")
async def handle_incoming():
    pass

@router.get("/webhook")
async def verify_Webhook():
    pass