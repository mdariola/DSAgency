# /backend/tools/data_tools.py (VERSIÓN FINALÍSIMA)

import os
import pandas as pd
import io
import traceback
import sys
import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import dspy # <--- Importar dspy aquí
import logging

from backend.agents.dspy_system import get_multi_agent_system

class DspyAnalysisToolSchema(BaseModel):
    user_question: str = Field(..., description="La pregunta específica del usuario sobre el conjunto de datos.")
    file_path: str = Field(..., description="La ruta al archivo CSV o Excel que debe ser analizado.")

class DspyAnalysisTool(BaseTool):
    name: str = "Análisis de Datos con DSPy"
    description: str = "..."
    args_schema: Type[BaseModel] = DspyAnalysisToolSchema

    def _clean_code(self, code: str) -> str:
        # ... (esta función se queda igual)
        if "```python" in code:
            return code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            return code.split("```")[1].split("```")[0].strip()
        return code.strip()

    def _run(self, user_question: str, file_path: str) -> str:
        logging.warning(f"RUTA RECIBIDA POR LA HERRAMIENTA: '{file_path}'")
        print(f"--- ⚒️ DspyAnalysisTool (v4-Inyección) iniciada: '{user_question}' ---")
        
        try:
            # --- INICIO DE LA MODIFICACIÓN CLAVE ---
            # 1. Configurar el LLM para DSPy AQUÍ MISMO, dentro de la herramienta.
            # Esto asegura que SIEMPRE se use la configuración correcta.
            llm_for_dspy = dspy.LiteLLM(
                model="gpt-4o-mini",
                api_base="http://litellm-proxy:4000",
                api_key="sk-irrelevant"
            )
            dspy.settings.configure(lm=llm_for_dspy)
            print("--- ✅ DSPy configurado localmente para usar el proxy de LiteLLM. ---")
            # --- FIN DE LA MODIFICACIÓN CLAVE ---
            
            # El resto del código que ya tenías para ejecutar el análisis...
            if not file_path or not os.path.exists(file_path):
                return "Error: La ruta del archivo no es válida o el archivo no existe."
            
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            dspy_system = get_multi_agent_system()
            agent_to_use = "planner_statistical_analytics_agent"
            plan_instructions = json.dumps({
                agent_to_use: {
                    "create": ["final_answer_summary"],
                    "use": ["df"],
                    "instruction": f"Calcula lo siguiente y escribe el código para imprimir el resultado final: {user_question}"
                }
            })
            agent_inputs = {
                "dataset": "El DataFrame está disponible como 'df'.",
                "goal": user_question,
                "plan_instructions": plan_instructions
            }

            print(f"--- 🧠 Invocando al agente DSPy '{agent_to_use}'... ---")
            statistical_agent_module = getattr(dspy_system, agent_to_use)
            result = statistical_agent_module(**agent_inputs)
            
            if not hasattr(result, 'code') or not result.code:
                return "Error: El sistema DSPy no generó el código de análisis necesario."
            
            generated_code = self._clean_code(result.code)
            print(f"--- 💻 Código generado por DSPy ---\n{generated_code}\n---------------------------------")
            
            output_buffer = io.StringIO()
            global_vars = {'df': df, 'pd': pd}
            old_stdout = sys.stdout
            sys.stdout = output_buffer
            
            try:
                exec(generated_code, global_vars)
                execution_result = output_buffer.getvalue().strip()
            finally:
                sys.stdout = old_stdout

            print(f"--- ✅ Resultado de la ejecución: '{execution_result}' ---")
            
            if not execution_result:
                return f"El código se ejecutó sin errores pero no produjo una salida."
            
            return f"La respuesta a '{user_question}' es: {execution_result}"

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"--- ❌ Error en DspyAnalysisTool: {error_trace} ---")
            return f"Ocurrió un error crítico durante el análisis: {str(e)}"