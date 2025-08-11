# En backend/tools/web_search_tool.py

import os
import json
import requests
from crewai import Agent, Task
from crewai.tools import BaseTool

class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "Realiza una búsqueda en internet sobre un tema específico y devuelve los resultados en un formato JSON estructurado."

    def _run(self, query: str) -> str:
        """
        Ejecuta la búsqueda web usando la API de Serper.
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: La clave de API de Serper (SERPER_API_KEY) no está configurada."

        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status() # Lanza un error para respuestas no exitosas (4xx o 5xx)
            search_results = response.json()

            # Formateamos los resultados para que sean más legibles para la IA
            formatted_results = []
            if "organic" in search_results:
                for result in search_results["organic"][:5]: # Devolvemos los primeros 5 resultados
                    formatted_results.append({
                        "title": result.get("title"),
                        "link": result.get("link"),
                        "snippet": result.get("snippet")
                    })

            if not formatted_results:
                return "No se encontraron resultados relevantes."

            return json.dumps(formatted_results, indent=2)

        except requests.exceptions.RequestException as e:
            return f"Error al contactar la API de Serper: {e}"
        except Exception as e:
            return f"Ocurrió un error inesperado durante la búsqueda: {e}"