# /backend/managers/ai_manager.py (VERSIÓN CORREGIDA Y DINÁMICA)

from langchain_openai import ChatOpenAI
from typing import Optional
import logging

from backend.agents.agents import ProjectAgents
from crewai import Crew, Process, Task

logging.basicConfig(level=logging.INFO)

class AIManager:
    def __init__(self):
        # El manager ya no guarda un estado de LLM. Ahora es más simple.
        logging.info("AIManager initialized (ready for dynamic model requests).")

    def _get_llm_instance(self, model_full_name: str) -> ChatOpenAI:
        """
        FUNCIÓN CLAVE: Crea y devuelve una nueva instancia de ChatOpenAI bajo demanda,
        configurada para usar el proxy de LiteLLM con el modelo especificado.
        """
        return ChatOpenAI(
            model=model_full_name,
            # La base_url siempre apunta al proxy
            openai_api_base="http://litellm-proxy:4000",
            # La api_key es manejada por el proxy, por lo que este valor es irrelevante
            openai_api_key="sk-irrelevant",
            temperature=0.2
        )

    # La firma del método ahora incluye 'model' para saber cuál LLM crear
    def run_crew(self, user_input: str, dataset_context: str, conversation_history: str, file_path: Optional[str], model: str) -> str:
        logging.info(f"Executing crew with dynamically configured model: {model}")
        
        # 1. Crea la instancia del LLM justo para esta tarea específica
        try:
            llm_instance = self._get_llm_instance(model)
        except Exception as e:
            logging.error(f"FATAL: Failed to create LLM instance for model {model}. Details: {e}", exc_info=True)
            return f"Error: No se pudo crear el cliente de IA para el modelo {model}."

        # 2. Crea tus agentes usando la instancia de LLM recién creada
        agents_factory = ProjectAgents(llm=llm_instance)
        director_proyecto = agents_factory.project_director()
        analista_datos = agents_factory.data_analyst()
        investigador_web = agents_factory.web_researcher()
        visualizador_datos = agents_factory.data_visualization_expert()
        cientifico_datos = agents_factory.predictive_modeler()

        # 3. Construye el contexto completo (tu lógica aquí es perfecta)
        file_context_info = ""
        if file_path:
            file_context_info = f"""
INFORMACIÓN DEL ARCHIVO A ANALIZAR:
---
La ruta ABSOLUTA del archivo que el usuario ha cargado es: '{file_path}'
Cualquier agente que necesite leer o analizar el archivo DEBE usar esta ruta exacta.
---
"""
        full_context = f"""{file_context_info}
CONTEXTO DEL CONJUNTO DE DATOS (resumen):
---
{dataset_context}
---
HISTORIAL DE LA CONVERSACIÓN ANTERIOR:
---
{conversation_history}
---
NUEVA PETICIÓN DEL USUARIO:
{user_input}"""

        # 4. Define la tarea y el Crew (sin cambios)
        project_management_task = Task(
            description=full_context,
            expected_output="Una respuesta final y completa que satisfaga la petición del usuario, basada en la colaboración del equipo.",
            agent=director_proyecto,
        )

        crew = Crew(
            agents=[director_proyecto, analista_datos, investigador_web, visualizador_datos, cientifico_datos],
            tasks=[project_management_task],
            process=Process.sequential,
            verbose=True
        )

        crew_output = crew.kickoff()
        
        if hasattr(crew_output, 'raw'):
            return crew_output.raw
        return str(crew_output)