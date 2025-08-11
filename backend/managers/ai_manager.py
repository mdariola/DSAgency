# Archivo: backend/managers/ai_manager.py (Versión Final y Corregida)

import dspy
from langchain_openai import ChatOpenAI
from typing import Optional, Dict, Any
import logging

class AIManager:
    def __init__(self):
        """Inicializa el manager."""
        self.dspy_lm = None
        self.chat_client = None
        self.configured = False
        self.current_provider = None
        self.current_model = None
        self.api_base = None
        logging.basicConfig(level=logging.INFO)

    def configure_model_with_proxy(self, model: str, api_base: str, api_key: str):
        """Configura el modelo inicial usando el proxy."""
        self.api_base = api_base
        try:
            # El proxy de LiteLLM usa el 'model_name' del config.yaml (el nombre corto)
            # No necesitamos añadir el prefijo del proveedor aquí.
            self.chat_client = ChatOpenAI(
                model=model,
                openai_api_base=api_base,
                openai_api_key=api_key,
                temperature=0.7
            )
            self.dspy_lm = dspy.LM(
                model=model,
                api_base=api_base,
                api_key=api_key
            )
            dspy.configure(lm=self.dspy_lm)

            # Asumimos que el modelo inicial es de openai para empezar
            self.current_provider = "openai"
            self.current_model = model
            self.configured = True

            logging.info("AIManager configured successfully with chat_client and dspy_lm via proxy.")
            return {"status": "success"}
        except Exception as e:
            self.configured = False
            logging.error(f"ERROR: AIManager failed to configure. Details: {e}", exc_info=True)
            raise e

    def configure_model(self, provider: str, model: str):
        """Re-configura los clientes con un nuevo modelo, pero re-usa el proxy existente."""
        if not self.api_base:
            return {"status": "error", "error": "Proxy not configured initially."}

        try:
            # CORRECCIÓN: Pasamos solo el nombre del modelo al cliente, sin el prefijo del proveedor.
            # LiteLLM se encarga de mapear este alias al modelo real.
            self.chat_client = ChatOpenAI(
                model=model,
                openai_api_base=self.api_base,
                openai_api_key="sk-irrelevant" # La API key es irrelevante para el proxy aquí
            )
            self.dspy_lm = dspy.LM(
                model=model,
                api_base=self.api_base,
                api_key="sk-irrelevant"
            )
            dspy.configure(lm=self.dspy_lm)

            self.current_provider = provider
            self.current_model = model
            self.configured = True
            
            logging.info(f"AIManager re-configured by user to use {model}")
            return {"status": "success"}
        except Exception as e:
            logging.error(f"Failed to re-configure model to {model}: {e}")
            return {"status": "error", "error": str(e)}

    def generate_response(self, messages: list, model: Optional[str] = None) -> str:
        if not self.is_configured() or not self.chat_client:
            raise Exception("AIManager is not configured. Cannot generate response.")
        try:
            # Usamos el modelo que se pasa o el actual, que ya es el nombre corto.
            effective_model = model or self.current_model
            response = self.chat_client.invoke(messages, model=effective_model)
            return response.content
        except Exception as e:
            logging.error(f"ERROR generating response: {e}", exc_info=True)
            return "Error: I'm having trouble generating a response at the moment."

    def get_available_models(self) -> dict:
        # Esta función solo alimenta al frontend, así que puede mantener la estructura con prefijos.
        model_ids = ["openai/gpt-4o-mini", "anthropic/claude-3-5-sonnet"]
        formatted_models = {}
        for model_id in model_ids:
            try:
                provider, model_name = model_id.split('/')
                if provider not in formatted_models:
                    formatted_models[provider] = []
                formatted_models[provider].append(model_name)
            except ValueError:
                logging.warning(f"Model ID '{model_id}' has wrong format.")
        return formatted_models

    def is_configured(self) -> bool:
        return self.configured

    def get_current_config(self) -> Dict[str, Any]:
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "configured": self.configured
        }
