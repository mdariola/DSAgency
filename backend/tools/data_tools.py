import os
import pandas as pd
import io
import traceback
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Importamos la función que nos da acceso a la instancia única de nuestro sistema DSPy
from backend.agents.dspy_system import get_multi_agent_system

class DspyAnalysisToolSchema(BaseModel):
    """Input schema for the DSPy Analysis Tool."""
    user_question: str = Field(..., description="La pregunta específica del usuario sobre el conjunto de datos.")
    file_path: str = Field(..., description="La ruta al archivo CSV o Excel que debe ser analizado.")

class DspyAnalysisTool(BaseTool):
    name: str = "Análisis de Datos con DSPy"
    description: str = """Útil para cuando necesitas responder preguntas complejas sobre un conjunto de datos específico. 
    Esta herramienta toma la pregunta de un usuario y la ruta a un archivo (CSV o Excel) para realizar un análisis profundo."""
    args_schema: Type[BaseModel] = DspyAnalysisToolSchema

    def _run(self, user_question: str, file_path: str) -> str:
        print(f"--- ⚒️ DspyAnalysisTool iniciada con la pregunta: '{user_question}' y el archivo: '{file_path}' ---")

        if not file_path or not os.path.exists(file_path):
            return "Error: No se proporcionó una ruta de archivo válida o el archivo no existe. No puedo realizar el análisis sin datos."

        try:
            # Leer el archivo con pandas
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return "Error: Formato de archivo no soportado. Por favor, usa CSV o Excel."

            # Generar un resumen detallado del DataFrame
            buffer = io.StringIO()
            df.info(buf=buffer)
            info_str = buffer.getvalue()
            
            head_str = df.head().to_string()
            describe_str = df.describe().to_string()

            dataset_context = f"""
            Resumen del conjunto de datos '{os.path.basename(file_path)}':
            - Primeras filas:
            {head_str}

            - Información de columnas:
            {info_str}

            - Estadísticas descriptivas:
            {describe_str}
            """
            
            print("--- 📝 Contexto generado para DSPy ---")
            print("------------------------------------")
            print("--- 🧠 Invocando al sistema DSPy (auto_analyst)... ---")
            
            # --- CÓDIGO CORREGIDO Y FINAL ---
            # 1. Obtenemos la instancia única de nuestro sistema DSPy
            dspy_system = get_multi_agent_system()
            
            # 2. Llamamos a su método `execute_workflow` que orquesta la planificación y ejecución
            response_dict = dspy_system.execute_workflow(user_query=user_question, available_data=dataset_context)
            
            # 3. Extraemos y formateamos la respuesta para que sea un string legible
            final_answer = response_dict.get("response", "El sistema de análisis no generó una respuesta.")
            if isinstance(final_answer, dict):
                final_answer = str(final_answer)

            print(f"--- ✅ Respuesta recibida de DSPy: {final_answer[:150]}... ---")
            return final_answer

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"--- ❌ Error en DspyAnalysisTool: {error_trace} ---")
            return f"Ocurrió un error al procesar el archivo o al ejecutar el análisis: {e}"
