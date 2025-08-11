# En backend/api/model_routes.py
import httpx
import os
from fastapi import APIRouter, HTTPException
from backend.managers.global_managers import ai_manager
from backend.utils.logger import Logger

# Asegúrate de tener estas variables definidas al principio del archivo
router = APIRouter(prefix="/api/models", tags=["models"])
logger = Logger("model_routes")


@router.get("/providers")
async def get_model_providers():
    """
    Obtiene los proveedores y modelos disponibles directamente desde el proxy LiteLLM.
    """
    proxy_url = os.getenv("LITELLM_PROXY_URL", "http://litellm-proxy:4000")
    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-1234")
    headers = {"Authorization": f"Bearer {master_key}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{proxy_url}/model/info", headers=headers)
            response.raise_for_status()
            model_data = response.json()

        providers = {}
        if "data" in model_data:
            for model in model_data["data"]:
                provider_name = model.get("id", "unknown").split('/')[0]
                model_id = model.get("model_name", "unknown")

                if provider_name not in providers:
                    providers[provider_name] = {
                        "name": provider_name,
                        "display_name": provider_name.title(),
                        "models": []
                    }
                
                providers[provider_name]["models"].append({
                    "id": model_id,
                    "name": model_id
                })
        
        current_config = ai_manager.get_current_config()

        return {
            "providers": list(providers.values()),
            "current_provider": current_config.get("provider"),
            "current_model": current_config.get("model")
        }

    except httpx.RequestError as e:
        logger.log_message(f"Error al conectar con el proxy de LiteLLM: {e}", "ERROR")
        raise HTTPException(status_code=503, detail="No se pudo conectar con el proxy de modelos.")
    except Exception as e:
        logger.log_message(f"Error procesando los proveedores de modelos: {e}", "ERROR")
        raise HTTPException(status_code=500, detail="Error al obtener los proveedores de modelos.")


@router.get("/current")
async def get_current_model():
    """
    Devuelve el objeto completo del proveedor activo y el nombre del modelo actual.
    """
    if not ai_manager.is_configured():
        raise HTTPException(status_code=404, detail="AI model is not configured yet.")
    
    current_config = ai_manager.get_current_config()
    current_provider_name = current_config.get("provider")
    current_model_name = current_config.get("model")

    # Obtenemos la lista completa de proveedores para encontrar el objeto correcto
    all_providers_response = await get_model_providers()
    all_providers = all_providers_response.get("providers", [])

    provider_object = next((p for p in all_providers if p['name'] == current_provider_name), None)

    if not provider_object:
         raise HTTPException(status_code=404, detail=f"Provider '{current_provider_name}' not found.")

    return {
        "provider": provider_object,
        "model": current_model_name
    }


@router.get("/api-keys/status")
async def get_api_keys_status():
    """
    Verifica y devuelve el estado de las claves API en las variables de entorno.
    """
    api_keys_status = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "serper": bool(os.getenv("SERPER_API_KEY")),
    }
    return api_keys_status

