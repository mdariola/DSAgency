# /backend/api/chat_routes.py (VERSIÓN FINAL CONECTADA)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback

from backend.managers.global_managers import session_manager, ai_manager

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def handle_chat_message(request: ChatRequest):
    try:
        session = session_manager.get_or_create_session(request.session_id)
        
        # Recuperamos TODOS los datos necesarios de la sesión
        file_path = session.get("file_path")
        dataset_context = session.get("dataset_context", "")
        conversation_history = session.get("conversation_history", "")

        # --- INICIO DE LA CORRECCIÓN ---

        # 1. OBTÉN EL MODELO DE LA SESIÓN
        #    Esta línea lee el modelo que el usuario guardó con el ModelSelector.
        #    Si no ha guardado ninguno, usa 'openai/gpt-4o-mini' como default.
        current_model = session.get('current_model', 'openai/gpt-4o-mini')

        # Ejecutamos el crew, ahora sí, pasándole TODOS los parámetros requeridos.
        result = ai_manager.run_crew(
            user_input=request.message,
            file_path=file_path,
            dataset_context=dataset_context,
            conversation_history=conversation_history,
            model=current_model  # <-- 2. PASA EL MODELO AL AIManager
        )

        # --- FIN DE LA CORRECCIÓN ---

        # Actualizamos el historial de la conversación (tu lógica aquí es perfecta)
        new_history_entry = f"User: {request.message}\nAssistant: {result}\n"
        updated_history = conversation_history + new_history_entry
        
        session_manager.update_context(request.session_id, {
            "conversation_history": updated_history
        })

        # Devolvemos la respuesta
        return {"response": result}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al procesar el mensaje: {str(e)}")