# /backend/agents/__init__.py (Versión Final y Corregida)

# 1. Importa la NUEVA CLASE 'ProjectAgents' desde agents.py
from .agents import ProjectAgents

# 2. Mantenemos las importaciones de tu sistema DSPy, ya que son necesarias
from .dspy_system import (
    get_multi_agent_system,
    auto_analyst,
    auto_analyst_ind,
    get_agent_description,
    AGENTS_WITH_DESCRIPTION,
    PLANNER_AGENTS_WITH_DESCRIPTION
)

# 3. Actualizamos la lista de exportación: quitamos lo viejo, añadimos lo nuevo.
__all__ = [
    'ProjectAgents',  # <-- AÑADIDO
    'get_multi_agent_system',
    'auto_analyst',
    'auto_analyst_ind',
    'get_agent_description',
    'AGENTS_WITH_DESCRIPTION',
    'PLANNER_AGENTS_WITH_DESCRIPTION'
    # 'get_data_analysis_crew' ha sido ELIMINADO de esta lista
]