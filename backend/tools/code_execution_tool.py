# /backend/tools/code_execution_tool.py (Versión a prueba de balas)

import os
import traceback
import pandas as pd
import plotly.express as px
import uuid
import re
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

CHARTS_DIR = "static/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

class CodeExecutionToolSchema(BaseModel):
    code: str = Field(..., description="El código Python a ejecutar para generar un gráfico con Plotly.")
    context: str = Field(..., description="El contexto completo que contiene la ruta del archivo y otros detalles del dataset.")

class CodeExecutionTool(BaseTool):
    name: str = "Ejecutor de Código Python para Gráficos"
    description: str = """Ejecuta código Python para generar visualizaciones de datos con Plotly."""
    args_schema: Type[BaseModel] = CodeExecutionToolSchema

    def _find_file_path(self, context: str) -> str | None:
        """Usa una expresión regular para encontrar de forma fiable la ruta del archivo buscando la etiqueta 'file_path:'."""
        # Busca el patrón "file_path: uploads/..." y captura la ruta.
        match = re.search(r"file_path:\s*(uploads/[a-zA-Z0-9\-_./]+\.(csv|xlsx|xls))", context)
        if match:
            return match.group(1).strip()
        return None

    def _run(self, code: str, context: str) -> str:
        file_path = self._find_file_path(context)
        
        print(f"--- ⚒️ CodeExecutionTool iniciada ---")
        print(f"--- 🔍 Buscando 'file_path:' en el contexto... Encontrada: '{file_path}' ---")

        if not file_path or not os.path.exists(file_path):
            return f"Error: No se pudo encontrar una etiqueta 'file_path:' con una ruta válida en el contexto o el archivo no existe. Contexto recibido: {context[:250]}..."

        try:
            df = pd.read_csv(file_path)
            local_namespace = {'df': df, 'px': px}
            exec(code, {}, local_namespace)

            if 'fig' not in local_namespace:
                return "Error: El código no generó una figura de Plotly en la variable 'fig'."

            fig = local_namespace['fig']
            unique_filename = f"chart_{uuid.uuid4()}.html"
            chart_path = os.path.join(CHARTS_DIR, unique_filename)
            fig.write_html(chart_path)
            
            frontend_path = f"/charts/{unique_filename}"
            print(f"--- ✅ Gráfico guardado en: '{chart_path}' ---")
            
            return f"Gráfico generado exitosamente. La ruta para mostrarlo es: {frontend_path}"

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"--- ❌ Error ejecutando código: {error_trace} ---")
            return f"Ocurrió un error al ejecutar el código de Python: {e}\nTraceback:\n{error_trace}"