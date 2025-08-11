# En backend/agents/__init__.py

# Importa la nueva función de CrewAI desde agents.py
from .agents import get_data_analysis_crew

# Importa el sistema DSPy desde dspy_system.py
from .dspy_system import (
    get_multi_agent_system,
    auto_analyst,
    auto_analyst_ind,
    get_agent_description,
    AGENTS_WITH_DESCRIPTION,
    PLANNER_AGENTS_WITH_DESCRIPTION
)

# No es estrictamente necesario, pero es una buena práctica
# definir qué se exporta desde este paquete.
__all__ = [
    'get_data_analysis_crew',
    'get_multi_agent_system',
    'auto_analyst',
    'auto_analyst_ind',
    'get_agent_description',
    'AGENTS_WITH_DESCRIPTION',
    'PLANNER_AGENTS_WITH_DESCRIPTION'
]