# /backend/api/model_routes.py (VERSIÓN CORREGIDA Y COMPLETA)

import os
import httpx
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

# Importa el gestor de sesiones global
from backend.managers.global_managers import session_manager

router = APIRouter(tags=["Models"])

# --- Pydantic Models para respuestas estructuradas ---
class ModelInfo(BaseModel):
    name: str

class ProviderInfo(BaseModel):
    name: str
    models: List[ModelInfo]

class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]

class CurrentModelResponse(BaseModel):
    provider: str
    model: str

class ConfigureModelRequest(BaseModel):
    provider: str
    model: str

# --- Endpoints ---

@router.get("/models/providers", response_model=ProvidersResponse)
async def get_model_providers():
    proxy_url = "http://litellm-proxy:4000/v1/models"
        # --- INICIO DE LA CORRECCIÓN ---
    # 1. Definimos la llave maestra. Debe ser LA MISMA que en litellm-config.yaml
    master_key = "super-secreto-1234"
    
    # 2. Creamos el encabezado de autorización
    headers = {
             "Authorization": f"Bearer {master_key}"
    }
    # --- FIN DE LA CORRECCIÓN ---
    providers_dict = {}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(proxy_url, headers=headers)
            response.raise_for_status()
            model_list = response.json().get('data', [])
            
            for model_data in model_list:
                model_id = model_data.get('id', '')
                if '/' in model_id:
                    provider_name, model_name = model_id.split('/', 1)
                    if provider_name not in providers_dict:
                        providers_dict[provider_name] = []
                    providers_dict[provider_name].append(ModelInfo(name=model_name))
            
            response_data = [ProviderInfo(name=name, models=models) for name, models in providers_dict.items()]
            return ProvidersResponse(providers=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener proveedores: {e}")

# ¡ENDPOINT CLAVE QUE FALTABA!
@router.post("/models/configure")
async def configure_model(request: ConfigureModelRequest = Body(...), session_id: str = Query(...)):
    session = session_manager.get_or_create_session(session_id)
    full_model_name = f"{request.provider}/{request.model}"
    session['current_model'] = full_model_name
    logging.info(f"Session [{session_id}] model configured to: {full_model_name}")
    return {"message": f"Model configured to {full_model_name}"}

@router.get("/models/current", response_model=CurrentModelResponse)
async def get_current_model(session_id: str = Query(...)):
    session = session_manager.get_or_create_session(session_id)
    model_full_name = session.get('current_model', 'openai/gpt-4o-mini') # Default
    provider, model = model_full_name.split('/', 1)
    return CurrentModelResponse(provider=provider, model=model)

@router.get("/models/api-keys/status", response_model=Dict[str, bool])
async def get_api_keys_status():
    keys = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
    return {p: bool(os.getenv(v)) for p, v in keys.items()}