from fastapi import FastAPI
from routes import webhook_routes

app = FastAPI(title="Los Motes de la Magdalena Webhook", version="1.0.0")

app.include_router(webhook_routes.router)