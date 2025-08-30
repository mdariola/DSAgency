# /backend/api/analytics_routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import pandas as pd
import io
import os
import uuid
import traceback
from pathlib import Path

# Importamos nuestro session_manager global
from backend.managers.global_managers import session_manager
# Importamos la ruta absoluta correcta desde el nuevo archivo de configuración
from backend.config import UPLOADS_DIR

router = APIRouter(tags=["analytics"])

@router.post("/analytics/upload-dataset")
async def upload_dataset(session_id: str = Form(...), file: UploadFile = File(...)):
    """
    Sube un archivo, lo guarda, genera un resumen y limpia la sesión para un nuevo análisis.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Por favor, sube un CSV o Excel.")

    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOADS_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        buffer_info = io.StringIO()
        df.info(buf=buffer_info)
        info_str = buffer_info.getvalue()
        
        dataset_context = f"""
        Resumen del conjunto de datos '{file.filename}':
        - Primeras 5 filas:
        {df.head().to_string()}

        - Información de columnas y tipos de datos:
        {info_str}

        - Resumen estadístico:
        {df.describe().to_string()}
        """

        # --- ESTA ES LA SECCIÓN CORREGIDA Y UNIFICADA ---
        # Creamos un único diccionario con TODO el contexto de la nueva sesión.
        session_context = {
            "file_path": str(file_path),          # Usamos la variable correcta 'file_path'
            "dataset_context": dataset_context,
            "conversation_history": ""            # Reiniciamos el historial de conversación
        }
        # Hacemos UNA SOLA llamada para actualizar el contexto, asegurando la limpieza.
        session_manager.update_context(session_id, session_context)
        # --- FIN DE LA CORRECCIÓN ---
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "columns": df.columns.tolist(),
            "shape": list(df.shape),
            "preview": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"No se pudo procesar el archivo: {str(e)}")
    """
    Sube un archivo, lo guarda en una ruta absoluta, genera un resumen de texto y lo almacena 
    en la sesión del usuario junto con la ruta del archivo.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Por favor, sube un CSV o Excel.")

    # Usamos un nombre de archivo único y pathlib para construir la ruta absoluta
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Construimos la RUTA ABSOLUTA usando la variable importada de config.py
    file_path = UPLOADS_DIR / unique_filename

    try:
        # Guardamos el archivo en la ruta absoluta
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Leemos el archivo desde el disco para el análisis (más seguro)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Generamos el resumen de texto (contexto)
        buffer_info = io.StringIO()
        df.info(buf=buffer_info)
        info_str = buffer_info.getvalue()
        
        dataset_context = f"""
        Resumen del conjunto de datos '{file.filename}':
        - Primeras 5 filas:
        {df.head().to_string()}

        - Información de columnas y tipos de datos:
        {info_str}

        - Resumen estadístico:
        {df.describe().to_string()}
        """
        session_context = {
            "file_path": absolute_file_path,
            "dataset_context": dataset_context,
            "conversation_history": ""  # <-- ¡Esta es la clave! Reiniciamos el historial.
        }
        session_manager.update_context(session_id, session_context)

        # Guardamos la RUTA ABSOLUTA (como string) y el RESUMEN en la sesión
        session = session_manager.get_or_create_session(session_id)
        session_manager.update_context(session_id, {
            "file_path": str(file_path),
            "dataset_context": dataset_context
        })
        
        # Devolvemos una respuesta útil al frontend
        return {
            "session_id": session_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "columns": df.columns.tolist(),
            "shape": list(df.shape),
            "preview": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"No se pudo procesar el archivo: {str(e)}")