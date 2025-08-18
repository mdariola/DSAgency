# /backend/tools/web_search_tool.py (Versión CORREGIDA con fecha actual)

import os
import json
import requests
from crewai import Agent, Task
from crewai.tools import BaseTool
from datetime import datetime # <--- 1. Importamos la librería datetime

class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "Realiza una búsqueda en internet sobre un tema específico y devuelve los resultados en un formato JSON estructurado."

    def _run(self, query: str) -> str:
        """
        Ejecuta la búsqueda web usando la API de Serper, añadiendo contexto de la fecha actual.
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: La clave de API de Serper (SERPER_API_KEY) no está configurada."

        # --- 2. OBTENER LA FECHA ACTUAL ---
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # --- 3. CREAR UNA CONSULTA CONTEXTUALIZADA ---
        # Esto le da al motor de búsqueda (y al LLM que lo interpreta) el contexto temporal correcto.
        contextualized_query = f"Hoy es {current_date}. La búsqueda relevante para esta fecha es: {query}"
        
        print(f"--- 🌐 Búsqueda Web con Contexto de Fecha ---")
        print(f"Consulta original: {query}")
        print(f"Consulta contextualizada enviada a Serper: {contextualized_query}")
        print(f"-------------------------------------------")

        url = "https://google.serper.dev/search"
        # Usamos la consulta contextualizada en el payload
        payload = json.dumps({"q": contextualized_query})
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status() 
            search_results = response.json()

            # El resto del formateo de resultados sigue igual
            formatted_results = []
            if "organic" in search_results:
                for result in search_results["organic"][:5]:
                    formatted_results.append({
                        "title": result.get("title"),
                        "link": result.get("link"),
                        "snippet": result.get("snippet")
                    })

            if not formatted_results:
                return "No se encontraron resultados relevantes para la búsqueda."

            return json.dumps(formatted_results, indent=2)

        except requests.exceptions.RequestException as e:
            return f"Error al contactar la API de Serper: {e}"
        except Exception as e:
            return f"Ocurrió un error inesperado durante la búsqueda: {e}"