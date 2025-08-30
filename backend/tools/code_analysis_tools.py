# /backend/tools/code_analysis_tools.py (VERSIÓN FINAL Y ROBUSTA)

import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import io
import sys

# El esquema no cambia, sigue siendo correcto.
class CodeExecutorToolSchema(BaseModel):
    """Input schema for the Code Executor Tool."""
    code: str = Field(..., description="El código Python para ejecutar.")
    file_path: str = Field(..., description="La ruta al archivo CSV para cargar en el DataFrame 'df'.")

class PythonCodeExecutorTool(BaseTool):
    name: str = "Ejecutor de Código Python"
    description: str = """Ejecuta un bloque de código Python sobre un DataFrame cargado desde un archivo CSV. 
    El DataFrame está disponible como 'df'. El código debe terminar con una línea que imprima el resultado final."""
    args_schema: Type[BaseModel] = CodeExecutorToolSchema

    def _run(self, code: str, file_path: str) -> str:
        # --- LA ÚNICA LÍNEA QUE NECESITAS AÑADIR ---
        # Esta línea corrige los saltos de línea dobles (\\n) que a veces genera el LLM,
        # convirtiéndolos en saltos de línea simples (\n) que Python entiende.
        code = code.replace('\\n', '\n')
        # --- FIN DE LA MODIFICACIÓN ---
        
        try:
            df = pd.read_csv(file_path)
            
            # Capturar la salida estándar (el resultado de print())
            output_buffer = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = output_buffer
            
            try:
                # El código se ejecuta con 'df' disponible en su contexto
                exec(code, {'df': df, 'pd': pd})
                output = output_buffer.getvalue().strip()
            finally:
                # Restaurar la salida estándar
                sys.stdout = old_stdout

            if not output:
                return "El código se ejecutó sin errores, pero no imprimió ningún resultado."
            
            return f"El resultado de la ejecución es: {output}"

        except Exception as e:
            return f"Error al ejecutar el código: {e}"