# /backend/tools/__init__.py

from .web_search_tool import WebSearchTool
from .data_tools import DspyAnalysisTool
# --- LÍNEA AÑADIDA ---
from .code_execution_tool import CodeExecutionTool

__all__ = [
    "WebSearchTool",
    "DspyAnalysisTool",
    # --- LÍNEA AÑADIDA ---
    "CodeExecutionTool" 
]