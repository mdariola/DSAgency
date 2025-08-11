"""
DSAgency Auto-Analyst Managers Module

This module contains manager classes for handling AI configuration and sessions.
"""

# Usamos imports absolutos para mayor claridad y robustez
from backend.managers.ai_manager import AIManager
from backend.managers.session_manager import SessionManager

__all__ = [
    "AIManager",
    "SessionManager"
]