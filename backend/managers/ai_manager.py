# /backend/managers/ai_manager.py (Corrección final para devolver solo el texto)

import dspy
from langchain_openai import ChatOpenAI
from typing import Optional, Dict, Any
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
            self.dspy_lm = dspy.LM(model=model, api_base=api_base, api_key=api_key)
            dspy.configure(lm=self.dspy_lm)
            self.configured = True
            logging.info("AIManager configured successfully via proxy.")
        except Exception as e:
            self.configured = False
            logging.error(f"ERROR: AIManager failed to configure. Details: {e}", exc_info=True)
            raise e

    def is_configured(self) -> bool:
        return self.configured

    def run_crew(self, user_input: str, dataset_context: str, conversation_history: str) -> str:
        if not self.is_configured():
            logging.error("FATAL: run_crew called but AIManager is not configured.")
            return "Error: El gestor de IA no está configurado. Revisa los logs de arranque del servidor."

        agents_factory = ProjectAgents(llm=self.chat_client)
        director_proyecto = agents_factory.project_director()
        analista_datos = agents_factory.data_analyst()
        investigador_web = agents_factory.web_researcher()
        visualizador_datos = agents_factory.data_visualization_expert()


        full_context = f"""CONTEXTO DEL CONJUNTO DE DATOS:\n---\n{dataset_context}\n---\n\nHISTORIAL DE LA CONVERSACIÓN ANTERIOR:\n---\n{conversation_history}\n---\n\nNUEVA PETICIÓN DEL USUARIO:\n{user_input}"""

        project_management_task = Task(
            description=full_context,
            expected_output="Una respuesta final y completa que satisfaga la petición del usuario, basada en la colaboración del equipo.",
            agent=director_proyecto,
        )

        crew = Crew(
            agents=[director_proyecto, analista_datos, investigador_web, visualizador_datos],
            tasks=[project_management_task],
            process=Process.sequential,
            verbose=True
        )

        crew_output = crew.kickoff()
        
        # --- LA CORRECCIÓN FINAL ESTÁ AQUÍ ---
        # En lugar de devolver todo el objeto, devolvemos solo el texto final.
        return crew_output.raw

ai_manager = AIManager()