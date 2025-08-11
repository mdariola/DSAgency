from crewai import Agent, Crew, Process
from backend.tools.web_search_tool import WebSearchTool
from backend.tools.data_tools import DspyAnalysisTool
from backend.managers.global_managers import ai_manager

# --- 1. Herramientas ---
web_search_tool = WebSearchTool()
dspy_analysis_tool = DspyAnalysisTool()

# --- 2. Agentes ---

investigador_web = Agent(
    role='Investigador Web de Hechos Concretos',
    goal='Encontrar datos específicos y verificables en la web usando tu herramienta. Devolver solo los datos crudos.',
    backstory='Eres un bot de búsqueda ultra-eficiente. Tu única función es ejecutar UNA búsqueda precisa y devolver los resultados.',
    tools=[web_search_tool],
    verbose=True,
    llm=ai_manager.chat_client
)

analista_de_datos = Agent(
    role='Analista de Datos Principal',
    goal='Realizar análisis de datos complejos sobre los datasets proporcionados, utilizando tu herramienta especializada.',
    backstory='Eres un analista de datos experto que utiliza un sistema de IA (DSPy) para ejecutar análisis profundos. Tu única función es recibir una tarea y ejecutarla con tu herramienta.',
    tools=[dspy_analysis_tool],
    verbose=True,
    llm=ai_manager.chat_client
)

director_proyecto = Agent(
    role='Asistente Principal de Proyectos de IA',
    goal=(
        "Actuar como un intermediario inteligente entre el usuario y los agentes especialistas. "
        "Tu función es interpretar la solicitud del usuario y delegarla correctamente al agente adecuado, "
        "asegurándote de que los argumentos para la delegación tengan el formato correcto."
    ),
    backstory=(
        "Eres un director de proyectos metódico. Tu ÚNICA función es delegar tareas a tus subordinados: "
        "'Investigador Web de Hechos Concretos' y 'Analista de Datos Principal'.\n\n"
        "--- PROCESO ESTRICTO ---\n"
        "1. Analiza la Tarea del usuario y el contexto disponible.\n"
        "2. Elige a cuál de los dos especialistas delegar el trabajo.\n"
        "3. Usa SIEMPRE la herramienta 'Delegate work to coworker' para pasarles la tarea.\n\n"
        
        "--- REGLAS CRÍTICAS PARA EL FORMATO DE DELEGACIÓN ---\n"
        "Al usar la herramienta 'Delegate work to coworker', el 'Action Input' DEBE ser un JSON con TRES claves:\n"
        "1. `coworker`: Un string con el nombre EXACTO del agente. (ej. 'Analista de Datos Principal').\n"
        "2. `task`: Un STRING SIMPLE Y DIRECTO que describa la tarea. (ej. 'Analiza los precios del archivo').\n"
        "3. `context`: Un STRING SIMPLE con TODA la información que el especialista necesita. Debes incluir el resumen del archivo y la ruta completa ('file_path') en este string.\n\n"
        
        "--- EJEMPLO DE FORMATO DE ENTRADA CORRECTO ---\n"
        "Action: Delegate work to coworker\n"
        "Action Input: {\n"
        "  \"coworker\": \"Analista de Datos Principal\",\n"
        "  \"task\": \"Analizar la correlación entre precio y área en el dataset.\",\n"
        "  \"context\": \"El resumen del dataset es [...]. La ruta del archivo es 'uploads/xyz.csv'.\"\n"
        "}\n\n"

        "--- ¡ERROR A EVITAR! ---\n"
        "NUNCA pases un diccionario como valor para 'task' o 'context'. SIEMPRE deben ser strings simples.\n"
        "INCORRECTO: \"task\": {\"description\": \"...\"}\n"
        "CORRECTO:   \"task\": \"...\""
    ),
    tools=[],
    allow_delegation=True,
    verbose=True,
    llm=ai_manager.chat_client
)

# --- 3. Definición de la Crew (Estructura Simplificada y Robusta) ---
def get_data_analysis_crew():
    return Crew(
        # Todos los agentes están ahora en la misma lista para una delegación clara.
        agents=[director_proyecto, investigador_web, analista_de_datos],
        tasks=[],
        # Usamos un proceso secuencial. La tarea inicial se le dará al director.
        process=Process.sequential,
        verbose=True,
        # Ya no se necesita un manager_agent, lo que elimina la fuente de errores de delegación.
    )
