# /backend/main.py

from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from backend.utils.logger import Logger
from backend.managers.global_managers import ai_manager
from backend.api import chat_routes, analytics_routes, model_routes
from fastapi.routing import APIRoute

logger = Logger("main", see_time=True, console_log=True)

# La configuración de UPLOADS_DIR se ha movido a backend/config.py para evitar importaciones circulares.

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.log_message("Starting DSAgency Auto-Analyst Backend", level=logging.INFO)
    try:
        # Aseguramos que el directorio de cargas exista (importando desde config)
        from backend.config import UPLOADS_DIR
        logger.log_message(f"Upload directory ensured at: {UPLOADS_DIR}", level=logging.INFO)
        
        logger.log_message("AI Manager is ready for dynamic model requests.", level=logging.INFO)

    
    except Exception as e:
        logger.log_message(f"FATAL: Failed to configure AI Manager with proxy: {e}", level=logging.CRITICAL)
    yield
    logger.log_message("Shutting down DSAgency Auto-Analyst Backend", level=logging.INFO)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE RUTAS CENTRALIZADA ---
app.include_router(chat_routes.router, prefix="/api")
app.include_router(analytics_routes.router, prefix="/api")
app.include_router(model_routes.router, prefix="/api")

# --- Montar archivos estáticos al final ---
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.on_event("startup")
async def startup_event():
    print("\n--- RUTAS REGISTRADAS EN FASTAPI ---")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"Ruta: {route.path}, Métodos: {route.methods}, Nombre: {route.name}")
    print("-------------------------------------\n")

