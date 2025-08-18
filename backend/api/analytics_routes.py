# /backend/api/analytics_routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import pandas as pd
import io
import os
import uuid
import traceback

# Importamos nuestro session_manager global
from backend.managers.global_managers import session_manager

# --- CORRECCIÓN: Se ha eliminado el 'prefix="/api/analytics"' de esta línea ---
# Ahora main.py se encarga de gestionar el prefijo "/api" para todas las rutas.
router = APIRouter(tags=["analytics"])

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

@router.post("/analytics/upload-dataset")
async def upload_dataset(session_id: str = Form(...), file: UploadFile = File(...)):
    """
    Sube un archivo, lo guarda, genera un resumen de texto y lo almacena 
    en la sesión del usuario junto con la ruta del archivo.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Por favor, sube un CSV o Excel.")

    # Usamos un nombre de archivo único para evitar conflictos
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, unique_filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # --- LÓGICA CENTRAL ---
        # 1. Leer el archivo con pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # 2. Generar el resumen de texto (contexto)
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        dataset_context = f"""
        Resumen del conjunto de datos '{file.filename}':
        - Primeras 5 filas:
        {df.head().to_string()}

        - Información de columnas y tipos de datos:
        {info_str}

        - Resumen estadístico:
        {df.describe().to_string()}
        """

        # 3. Guardar la RUTA y el RESUMEN en la sesión del usuario
        session = session_manager.get_or_create_session(session_id)
        session_manager.update_context(session_id, {
            "file_path": file_path,
            "dataset_context": dataset_context
        })
        
        # 4. Devolver una respuesta útil al frontend
        return {
            "session_id": session_id,
            "filename": file.filename,
            "file_path": file_path,
            "columns": df.columns.tolist(),
            "shape": list(df.shape),
            "preview": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"No se pudo procesar el archivo: {str(e)}")

