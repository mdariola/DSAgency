# /backend/api/chat_routes.py

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
import traceback

# Importaciones clave para la lógica de la aplicación
from backend.managers.global_managers import session_manager, ai_manager

# --- CORRECCIÓN CLAVE: El prefijo "/api" se gestiona en main.py ---
# El router aquí no necesita prefijo, solo etiquetas.
router = APIRouter(tags=["chat"])

# --- MEJORA: Usar Pydantic para validar los datos de entrada ---
# Esto hace que la API sea más robusta y clara.
class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def handle_chat_message(request: ChatRequest):
    """
    Gestiona un mensaje de chat del usuario.
    1. Recupera la sesión y el contexto existente (historial, info del archivo).
    2. Ejecuta el equipo de agentes con el contexto completo.
    3. Actualiza el historial de la conversación en la sesión.
    4. Devuelve la respuesta del agente.
    """
    try:
        # 1. Recuperar el contexto de la sesión
        session = session_manager.get_or_create_session(request.session_id)
        
        # Obtenemos tanto el contexto del archivo como el historial de la conversación
        dataset_context = session.get("dataset_context", "")
        conversation_history = session.get("conversation_history", "")

        # 2. Ejecutar el equipo de agentes
        # Aquí pasamos TODO el contexto relevante al Director de Proyectos.
        result = ai_manager.run_crew(
            user_input=request.message,
            dataset_context=dataset_context,
            conversation_history=conversation_history
        )

        # 3. Actualizar la memoria a corto plazo (historial)
        new_history_entry = f"User: {request.message}\nAssistant: {result}\n"
        updated_history = conversation_history + new_history_entry
        
        session_manager.update_context(request.session_id, {
            "conversation_history": updated_history
        })

        # 4. Devolver la respuesta al frontend
        return {"response": result}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al procesar el mensaje: {str(e)}")