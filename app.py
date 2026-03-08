from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from database.database import init_db
from routes import webhook_routes
from services.intent_classifier import init_classifier


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicializa la base de datos y el clasificador de intenciones al arrancar
    """
    logging.info("Iniciando aplicación...")
    init_db()
    logging.info("Base de datos inicializada")
    
    # Inicializar clasificador de intenciones
    if await init_classifier():
        logging.info("Clasificador de intenciones cargado")
    else:
        logging.warning("Clasificador no disponible - usando fallback para mensajes de texto")
    
    yield


app = FastAPI(
    title="Los Motes de la Magdalena Webhook",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook_routes.router)