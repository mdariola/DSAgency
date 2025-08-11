from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime

from backend.agents.agents import get_data_analysis_crew, director_proyecto
from crewai import Task
from backend.managers.global_managers import ai_manager, session_manager
from backend.schemas.query_schemas import QueryRequest, QueryResponse
import traceback

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Punto de entrada principal que ahora usa el sistema de CrewAI para orquestar la respuesta.
    """
    try:
        if not ai_manager.is_configured():
            raise HTTPException(status_code=500, detail="AI model not configured. Check server startup logs.")

        session_id = request.session_id or str(uuid.uuid4())
        session = session_manager.get_or_create_session(session_id)
        session_manager.add_message(session_id, {"role": "user", "content": request.message})

        # --- CAMBIO CLAVE: OBTENER CONTEXTO DEL ARCHIVO DESDE LA SESIÓN ---
        session_context = session.get('context', {})
        file_path = session_context.get('file_path', None)
        dataset_context = session_context.get('dataset_context', "No hay un archivo cargado.")
        
        current_date = datetime.now().strftime("%d de %B de %Y")
        
        # Preparamos los inputs para la tarea de la Crew
        inputs = {
            'user_query': request.message,
            'file_path': file_path,
            'dataset_context': dataset_context,
            'current_date': current_date
        }

        data_crew = get_data_analysis_crew()
        
        analysis_task = Task(
            description=(
                "**Fecha actual:** {current_date}.\n"
                "**Pregunta del usuario:** '{user_query}'.\n"
                "**Contexto del dataset disponible:** {dataset_context}\n"
                "**Ruta del archivo (si existe):** '{file_path}'.\n\n"
                "**Instrucciones de Razonamiento y Delegación:**\n"
                "1. **Analiza la intención del usuario:** ¿Está pidiendo una acción específica (ej. 'analiza', 'dime la media', 'crea un gráfico') o solo está verificando una capacidad (ej. 'puedes ver', 'tienes acceso a')?\n"
                "2. **Si el usuario SOLO pregunta si puedes 'ver' o 'acceder' al archivo:** Responde afirmativamente, indicando el nombre del archivo que ves en el contexto, y pregúntale qué le gustaría hacer a continuación. NO uses ninguna herramienta.\n"
                "3. **Si el usuario pide una ACCIÓN sobre el archivo:** Delega la tarea al 'Analista de Datos Principal', pasándole la pregunta completa y la ruta exacta del archivo ('{file_path}').\n"
                "4. **Si la pregunta es general o requiere info de internet:** Delega al 'Investigador Web de Hechos Concretos'.\n"
                "5. **Si es un saludo:** Responde amablemente sin usar herramientas."
            ),
            expected_output='Una respuesta conversacional y útil que responda directamente al usuario, o el resultado de la tarea delegada.',
            agent=director_proyecto
        )


        data_crew.tasks = [analysis_task]
        crew_output = data_crew.kickoff(inputs=inputs)
        result = str(crew_output)

        session_manager.add_message(session_id, {"role": "assistant", "content": result})
        model_used_str = f"{ai_manager.get_current_config().get('provider')}/{ai_manager.get_current_config().get('model')}"

        return QueryResponse(
            response=result,
            session_id=session_id,
            model_used=model_used_str
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
