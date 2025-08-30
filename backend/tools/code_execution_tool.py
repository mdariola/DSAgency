# /backend/tools/code_execution_tool.py (VERSIÓN FINAL Y SIMPLIFICADA)

import os
import traceback
import pandas as pd
import plotly.express as px
import uuid
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

CHARTS_DIR = "static/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- CAMBIO 1: El Esquema ahora pide 'file_path' directamente, igual que la otra herramienta ---
class GraphingToolSchema(BaseModel):
    """Input schema for the Graphing Tool."""
    code: str = Field(..., description="El código Python a ejecutar para generar un gráfico con Plotly.")
    file_path: str = Field(..., description="La ruta absoluta al archivo CSV que debe ser analizado.")

class CodeExecutionTool(BaseTool):
    name: str = "Ejecutor de Código Python para Gráficos"
    description: str = """Ejecuta código Python para generar visualizaciones de datos con Plotly."""
    args_schema: Type[BaseModel] = GraphingToolSchema

    # --- CAMBIO 2: La función _run ahora acepta 'file_path' directamente ---
    def _run(self, code: str, file_path: str) -> str:
        
        # Añadimos la limpieza de código que nos faltaba
        code = code.replace('\\n', '\n')
        
        print(f"--- ⚒️ CodeExecutionTool (Gráficos) iniciada ---")
        print(f"--- 📄 Ruta de archivo recibida: '{file_path}' ---")

        if not file_path or not os.path.exists(file_path):
            return f"Error: La ruta del archivo '{file_path}' no es válida o el archivo no existe."

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
            print(f"--- ❌ Error ejecutando código de gráfico: {error_trace} ---")
            return f"Ocurrió un error al ejecutar el código para el gráfico: {e}"