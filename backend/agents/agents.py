from crewai import Agent
from langchain_openai import ChatOpenAI
from backend.tools.web_search_tool import WebSearchTool
from backend.tools.code_execution_tool import CodeExecutionTool

# --- ¡NUEVA IMPORTACIÓN! ---
from backend.tools.code_analysis_tools import PythonCodeExecutorTool

class ProjectAgents:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.web_search_tool = WebSearchTool()
        self.code_execution_tool = CodeExecutionTool()
        # --- ¡NUEVA HERRAMIENTA! ---
        self.python_code_executor_tool = PythonCodeExecutorTool()

    def project_director(self) -> Agent:
        # ... (este agente no cambia)
        return Agent(
            role='Asistente Principal de Proyectos de IA',
            goal=(
                "Actuar como un intermediario inteligente entre el usuario y los agentes especialistas. "
                "Tu función es interpretar la solicitud del usuario y delegarla correctamente al agente adecuado."
            ),
            backstory=(
                "Eres un director de proyectos metódico y ultra-preciso. Tu trabajo es analizar las peticiones y delegarlas a tu equipo.\n\n"
                "--- REGLA DE ORO ---\n"
                "Si la petición del usuario es un saludo, una despedida, o una pregunta simple, "
                "respóndele directamente de forma amable y concisa. NO DELEGUES estas interacciones.\n\n"
                "Para todas las demás peticiones, sigue tu proceso estricto:\n"
                "--- PROCESO ESTRICTO ---\n"
                "1. Analiza la Tarea del usuario y el contexto disponible.\n"
                "2. Elige a cuál de tus especialistas delegar el trabajo.\n"
                "3. USA SIEMPRE la herramienta 'Delegate work to coworker'.\n\n"
                "--- REGLAS CRÍTICAS PARA EL FORMATO DE DELEGACIÓN ---\n"
                "Al usar 'Delegate work to coworker', el 'Action Input' debe ser un JSON con TRES claves: `coworker`, `task`, y `context`.\n"
                "Los valores para `task` y `context` DEBEN ser STRINGS SIMPLES.\n\n"
                                # --- INICIO DEL AJUSTE FINAL ---
                "**FORMATO OBLIGATORIO PARA EL CAMPO 'context':**\n"
                "El string que pases en el campo `context` DEBE contener la ruta COMPLETA del archivo que el usuario subió. "
                "La clave debe ser `file_path:`. ES CRÍTICO que esta ruta sea correcta para que los otros agentes puedan encontrar el archivo.\n\n"
                "**EJEMPLO DE UN `context` PERFECTO:**\n"
                "'file_path: uploads/f5e2c0b7-092c-4188-b2a8-ddb490919035_Housing.csv'"
                # --- FIN DEL AJUSTE FINAL ---
            ),
            tools=[],
            allow_delegation=True,
            verbose=True,
            llm=self.llm
        )

    # --- ¡AGENTE COMPLETAMENTE NUEVO! ---
    def data_analyst(self) -> Agent:
        return Agent(
            role='Experto Analista de Datos con Python',
            goal='Escribir y ejecutar código de Python para responder preguntas sobre un conjunto de datos proporcionado.',
            backstory=(
                "Eres un analista de datos senior especializado en Pandas. Tu única función es recibir una pregunta y la ruta a un archivo de datos, "
                "y responderla escribiendo y ejecutando código de Python.\n\n"
                "--- TU PROCESO ESTRICTO ---\n"
                "1. Recibes una 'task' (pregunta) y un 'context' (con 'file_path').\n"
                "2. Tu primer pensamiento es: '¿Qué código de pandas necesito para responder esto?'.\n"
                "3. Escribes un snippet de código. El DataFrame se cargará automáticamente como 'df'.\n"
                "4. Tu código DEBE terminar con una línea que imprima el resultado final. Ejemplo: `print(df['columna'].mean())`.\n"
                "5. Usas tu herramienta 'Ejecutor de Código Python', pasándole el 'code' que escribiste y el 'file_path' que recibiste."
                "6. El resultado de la herramienta es tu respuesta final."
            ),
            tools=[self.python_code_executor_tool], # <-- Usando la nueva herramienta
            verbose=True,
            llm=self.llm
        )
    
    def web_researcher(self) -> Agent:
        # ... (este agente no cambia)
        return Agent(
            role='Investigador Web de Hechos Concretos',
            goal='Encontrar datos específicos y verificables en la web usando tu herramienta. Devolver solo los datos crudos.',
            backstory='Eres un bot de búsqueda ultra-eficiente. Tu única función es ejecutar UNA búsqueda precisa y devolver los resultados.',
            tools=[self.web_search_tool],
            verbose=True,
            llm=self.llm
        )


    # --- 4. DEFINIMOS EL NUEVO AGENTE ---
    def data_visualization_expert(self) -> Agent:
        return Agent(
            role="Experto en Visualización de Datos",
            goal="Crear visualizaciones y gráficos de datos claros y efectivos usando Python y Plotly.",
            backstory=(
                "Eres un especialista en visualización de datos. Tu función es recibir una petición y generar el código Python para un gráfico.\n"
                "--- TU PROCESO ---\n"
                "1. Recibes una 'task' (ej. 'crea un gráfico de barras') y un 'context' del Director.\n"
                "2. Basado en la 'task', escribes el código de Plotly Express (px) necesario para generar la visualización. El DataFrame estará disponible como 'df'.\n"
                "3. Te aseguras de que el resultado de tu código sea una variable llamada 'fig' (ej. `fig = px.bar(...)`).\n"
                "4. Llamas a tu herramienta 'Ejecutor de Código Python para Gráficos' pasándole DIRECTAMENTE el 'contexto' que recibiste y el 'código' que generaste."
            ),
            tools=[self.code_execution_tool],
            verbose=True,
            llm=self.llm,
        )