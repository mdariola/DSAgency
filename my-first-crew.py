# my-first-crew.py
# MVP: CrewAI usando SOLO OpenAI (la ruta más estable y mínima)

import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Cargar variables de entorno
load_dotenv()

# --- Configuración del LLM para CrewAI (LiteLLM Proxy) ---
try:
    # El modelo y la clave ya no dependen de OpenAI directamente
    openai_model_name = "gpt-4o-mini"

    # Configuración del LLM para el Agente de CrewAI usando el proxy LiteLLM
    crewai_llm = ChatOpenAI(
        model=openai_model_name,
        openai_api_base="http://litellm-proxy:4000",
        openai_api_key="sk-irrelevant",  # El proxy gestiona la clave real
        temperature=0.7
    )
    print("CrewAI Agent LLM configurado para usar gpt-4o-mini a través del proxy LiteLLM.")

except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo configurar el LLM de LiteLLM Proxy. Error: {e}")
    print("No se puede continuar sin un LLM válido.")
    exit(1)

# --- Definir Agente y Tarea CrewAI ---
summarizer_agent = Agent(
    role="Experto en Resúmenes Técnicos",
    goal="Generar un resumen conciso de informes técnicos.",
    backstory=(
        "Eres un experto en sintetizar información y dar respuestas concisas. "
        "Tu objetivo es siempre entregar los puntos clave de manera clara y precisa."
    ),
    verbose=True,
    llm=crewai_llm
)

example_report = """
El impacto de la inteligencia artificial en la industria del acero ha sido significativo en los últimos años. Las plantas han adoptado sistemas de mantenimiento predictivo, optimización de procesos y control de calidad automatizado. Esto ha resultado en una reducción de costos, mejora en la eficiencia y una mayor seguridad para los trabajadores. Sin embargo, la integración de IA también presenta desafíos, como la necesidad de capacitación y la gestión del cambio organizacional.
"""

summarize_task = Task(
    description=f"""
    Resume el siguiente informe técnico en 3-4 puntos clave:
    {example_report}
    No añadas introducciones ni conclusiones extra, solo los puntos clave.
    """,
    agent=summarizer_agent,
    expected_output="Un resumen de 3-4 puntos clave del informe técnico sobre el impacto de la IA en la industria del acero."
)

# --- Crea y Ejecuta la Crew (Equipo) ---
crew = Crew(
    agents=[summarizer_agent],
    tasks=[summarize_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print("\n--- Iniciando la Crew de DSAgency (MVP) ---")
    result = crew.kickoff()
    print("\n########################################")
    print("## Proceso de la Crew Completado!    ##")
    print("########################################\n")
    print(result)
