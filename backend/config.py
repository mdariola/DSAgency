# /backend/config.py

import os
from pathlib import Path

# Definimos la ruta absoluta para las cargas aquí.
# Este archivo será la única fuente de verdad para las configuraciones compartidas.
UPLOADS_DIR = Path("/app/uploads")

# Nos aseguramos de que el directorio exista al iniciar.
os.makedirs(UPLOADS_DIR, exist_ok=True)