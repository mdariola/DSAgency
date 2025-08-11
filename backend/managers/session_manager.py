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
        self.sessions = {}  # In-memory storage for sessions
        self.active_sessions = set()
        
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new session.
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "messages": [],
            "context": {},
            "metadata": {}
        }
        
        self.active_sessions.add(session_id)
        logger.log_message(f"Created new session: {session_id}", level=logging.INFO)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        """
        return self.sessions.get(session_id)

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """
        Obtiene una sesión existente o crea una nueva si no se encuentra.
        """
        session = self.get_session(session_id)
        if session:
            return session
        
        # Si no se encontró la sesión, la creamos con ese ID específico
        logger.log_message(f"Session not found: {session_id}. Creating new one.", level=logging.INFO)
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "messages": [],
            "context": {},
            "metadata": {}
        }
        self.active_sessions.add(session_id)
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        Add a message to the session.
        """
        try:
            if session_id not in self.sessions:
                logger.log_message(f"Session not found: {session_id}", level=logging.WARNING)
                return False
            
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()
            
            self.sessions[session_id]["messages"].append(message)
            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            logger.log_message(f"Error adding message to session {session_id}: {str(e)}", level=logging.ERROR)
            return False
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from a session.
        """
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id]["messages"]
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def update_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """
        Update session context.
        """
        try:
            if session_id not in self.sessions:
                return False
            
            self.sessions[session_id]["context"].update(context)
            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            logger.log_message(f"Error updating context for session {session_id}: {str(e)}", level=logging.ERROR)
            return False
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get session context.
        """
        if session_id not in self.sessions:
            return {}
        
        return self.sessions[session_id]["context"]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                self.active_sessions.discard(session_id)
                logger.log_message(f"Deleted session: {session_id}", level=logging.INFO)
                return True
            
            return False
            
        except Exception as e:
            logger.log_message(f"Error deleting session {session_id}: {str(e)}", level=logging.ERROR)
            return False
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List sessions, optionally filtered by user.
        """
        sessions = []
        
        for session_id, session_data in self.sessions.items():
            if user_id is None or session_data.get("user_id") == user_id:
                sessions.append({
                    "session_id": session_id,
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data["created_at"],
                    "last_activity": session_data["last_activity"],
                    "message_count": len(session_data["messages"])
                })
        
        return sessions
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up inactive sessions older than specified age.
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        sessions_to_delete = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = datetime.fromisoformat(session_data["last_activity"])
            if last_activity < cutoff_time:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
        
        logger.log_message(f"Cleaned up {len(sessions_to_delete)} inactive sessions", level=logging.INFO)
        
        return len(sessions_to_delete)