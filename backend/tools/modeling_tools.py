import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
import joblib
import os
import uuid

# --- HERRAMIENTA 1: ENTRENAR Y GUARDAR MODELO (SIN CAMBIOS) ---
class ModelTrainingTool(BaseTool):
    name: str = "Entrenador de Modelos de Regresión"
    description: str = "..."
    args_schema: Type[BaseModel] = Field(..., description="Esquema de entrada para la herramienta de entrenamiento.")
    
    class ModelTrainingToolSchema(BaseModel):
        file_path: str = Field(..., description="La ruta al archivo CSV que contiene los datos.")
        target_column: str = Field(..., description="El nombre de la columna que el modelo debe predecir.")
        feature_columns: List[str] = Field(..., description="La lista de nombres de columnas para usar como características.")

    args_schema = ModelTrainingToolSchema

    def _run(self, file_path: str, target_column: str, feature_columns: List[str]) -> str:
        try:
            df = pd.read_csv(file_path)
            df_processed = pd.get_dummies(df, drop_first=True)
            
            final_feature_columns = []
            for feat in feature_columns:
                matching_cols = [col for col in df_processed.columns if feat in col]
                if matching_cols:
                    final_feature_columns.extend(matching_cols)
                elif feat in df_processed.columns:
                    final_feature_columns.append(feat)
            
            final_feature_columns = list(dict.fromkeys(final_feature_columns))
            df_processed.dropna(inplace=True)

            X = df_processed[final_feature_columns]
            y = df_processed[target_column]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)

            models_dir = "models"
            os.makedirs(models_dir, exist_ok=True)
            model_id = uuid.uuid4()
            model_path = os.path.join(models_dir, f"regression_model_{model_id}.pkl")
            joblib.dump(model, model_path)
            
            predictions = model.predict(X_test)
            r2 = r2_score(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))

            result = (
                f"¡Modelo de Regresión Lineal entrenado y guardado con éxito!\n"
                f"ID del Modelo: {model_id}\n"
                f"Ruta del Modelo: {model_path}\n\n"
                f"--- Métricas de Rendimiento ---\n"
                f"R-cuadrado (R²): {r2:.4f}\n"
                f"RMSE: {rmse:,.2f}"
            )
            return result
        except Exception as e:
            return f"Error durante el entrenamiento del modelo: {str(e)}"

# --- HERRAMIENTA 2: USAR UN MODELO PARA PREDECIR (VERSIÓN CORREGIDA Y ROBUSTA) ---
class ModelPredictionTool(BaseTool):
    name: str = "Herramienta de Predicción de Precios"
    description: str = "Usa un modelo de regresión previamente entrenado para predecir un valor a partir de nuevos datos."
    args_schema: Type[BaseModel] = Field(..., description="Esquema de entrada para la herramienta de predicción.")

    class ModelPredictionToolSchema(BaseModel):
        model_path: str = Field(..., description="La ruta al archivo del modelo guardado (.pkl).")
        new_data: Dict = Field(..., description="Un diccionario con los nuevos datos para la predicción. Ejemplo: {'area': 3000, 'bathrooms': 2}")

    args_schema = ModelPredictionToolSchema

    def _run(self, model_path: str, new_data: Dict) -> str:
        try:
            if not os.path.exists(model_path):
                return f"Error: No se encontró el archivo del modelo en la ruta: {model_path}"
            
            model = joblib.load(model_path)
            
            # --- INICIO DE LA LÓGICA DE CORRECCIÓN ---
            # 1. Obtener la lista de características que el modelo ESPERA
            expected_features = model.feature_names_in_
            
            # 2. Crear un DataFrame con los datos que el usuario nos dio
            new_df = pd.DataFrame([new_data])
            
            # 3. Alinear las columnas:
            # - Añadir cualquier columna que el modelo espere pero que no nos dieron, con un valor de 0.
            #   (ej. el modelo espera 'prefarea_yes', pero no la recibimos, así que asumimos que es 0)
            for col in expected_features:
                if col not in new_df.columns:
                    new_df[col] = 0
            
            # - Asegurarse de que las columnas están en el MISMO ORDEN y solo existen las que el modelo espera
            final_df = new_df[expected_features]
            # --- FIN DE LA LÓGICA DE CORRECCIÓN ---
            
            prediction = model.predict(final_df)
            
            return f"El precio predicho es: ${prediction[0]:,.2f}"
            
        except Exception as e:
            return f"Error durante la predicción: {str(e)}"