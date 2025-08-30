# /backend/managers/ai_manager.py (VERSIÓN FINAL CORREGIDA)

import dspy
from langchain_openai import ChatOpenAI
from typing import Optional
import logging

from backend.agents.agents import ProjectAgents
from crewai import Crew, Process, Task

class AIManager:
    def __init__(self):
        self.dspy_lm = None
        self.chat_client = None
        self.configured = False
        self.api_base = None
        self.current_provider = None
        self.current_model = None
        logging.basicConfig(level=logging.INFO)

    def configure_model_with_proxy(self, model: str, api_base: str, api_key: str):
        self.api_base = api_base
        try:
            self.chat_client = ChatOpenAI(model=model, openai_api_base=api_base, openai_api_key=api_key, temperature=0.2)
            # Nota: DSPy puede que no necesite reconfiguración en cada ejecución si el LLM es constante.
            # Esta configuración inicial puede ser suficiente.
            self.configured = True
            logging.info("AIManager configured successfully via proxy.")
        except Exception as e:
            self.configured = False
            logging.error(f"ERROR: AIManager failed to configure. Details: {e}", exc_info=True)
            raise e

    def is_configured(self) -> bool:
        return self.configured

    # --- INICIO DE LA MODIFICACIÓN CLAVE ---
    # 1. Añadimos 'file_path: Optional[str]' a la firma de la función.
    def run_crew(self, user_input: str, dataset_context: str, conversation_history: str, file_path: Optional[str]) -> str:
        if not self.is_configured():
            logging.error("FATAL: run_crew called but AIManager is not configured.")
            return "Error: El gestor de IA no está configurado. Revisa los logs de arranque del servidor."

        agents_factory = ProjectAgents(llm=self.chat_client)
        director_proyecto = agents_factory.project_director()
        analista_datos = agents_factory.data_analyst()
        investigador_web = agents_factory.web_researcher()
        visualizador_datos = agents_factory.data_visualization_expert()
        cientifico_datos = agents_factory.predictive_modeler()


        # 2. Construimos el contexto de forma inteligente.
        #    Añadimos la información de la ruta del archivo SOLO SI EXISTE.
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
        # --- FIN DE LA MODIFICACIÓN CLAVE ---

        project_management_task = Task(
            description=full_context,
            expected_output="Una respuesta final y completa que satisfaga la petición del usuario, basada en la colaboración del equipo.",
            agent=director_proyecto,
        )

        crew = Crew(
            agents=[director_proyecto, analista_datos, investigador_web, visualizador_datos,cientifico_datos],
            tasks=[project_management_task],
            process=Process.sequential,
            verbose=True
        )

        crew_output = crew.kickoff()
        
        # CrewAI v0.28.8+ devuelve un objeto, extraemos el resultado crudo.
        if hasattr(crew_output, 'raw'):
             return crew_output.raw
        return str(crew_output)