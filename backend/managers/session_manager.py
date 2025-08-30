# /backend/managers/session_manager.py

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime
from backend.utils.logger import Logger

logger = Logger("session_manager", see_time=True, console_log=False)

class SessionManager:
    """
    Manages user sessions, chat history, and conversation context.
    Handles session creation, message storage, and retrieval.
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """
        Obtiene una sesión existente o crea una nueva si no se encuentra.
        """
        session = self.sessions.get(session_id)
        if session:
            # Asegurarse de que las sesiones antiguas también tengan el historial
            session.setdefault("conversation_history", "")
            return session
        
        # Si no se encontró la sesión, la creamos con ese ID específico
        logger.log_message(f"Session not found: {session_id}. Creating new one.", level=logging.INFO)
        new_session = {
            "session_id": session_id,
            "user_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "messages": [],
            "context": {},
            "metadata": {},
            # --- CAMBIO CLAVE: AÑADIR HISTORIAL AL CREAR SESIÓN ---
            "conversation_history": "" 
        }
        self.sessions[session_id] = new_session
        return new_session
    
    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """
        Update session context. Can also be used to update conversation_history.
        """
        try:
            if session_id not in self.sessions:
                return False
            
            # Esto funcionará para 'file_context' y nuestro nuevo 'conversation_history'
            for key, value in context_updates.items():
                 self.sessions[session_id][key] = value

            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.log_message(f"Error updating context for session {session_id}: {str(e)}", level=logging.ERROR)
            return False

    def get_context_value(self, session_id: str, key: str) -> Optional[Any]:
        """
        Get a specific value from the session's context or main level.
        """
        if session_id in self.sessions:
            return self.sessions[session_id].get(key)
        return None
    

# Instancia global para ser usada en toda la aplicación
session_manager = SessionManager()