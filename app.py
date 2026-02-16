from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from database.database import init_db
from routes import webhook_routes


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicializa la base de datos al arrancar la aplicación
    """
    logging.info("Iniciando aplicación...")
    init_db()
    logging.info("Base de datos inicializada")
    yield


app = FastAPI(
    title="Los Motes de la Magdalena Webhook",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook_routes.router)