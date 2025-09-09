## DSAgency — Arquitectura y Workflow

### Resumen
Aplicación full‑stack para análisis de datos asistido por IA. El frontend (React) permite subir datasets, elegir proveedor/modelo LLM vía LiteLLM Proxy y conversar por chat. El backend (FastAPI) gestiona sesiones, archivos y orquesta agentes (CrewAI) con modelos servidos a través de LiteLLM.

### Componentes principales
- Frontend (React + Ant Design + Chakra): `ChatInterface`, `FileUploader`, `ModelSelector`.
- Backend (FastAPI): rutas `chat`, `analytics`, `models`, `upload` y gestores `SessionManager`, `AIManager`.
- Agentes (CrewAI): Director de Proyecto, Analista de Datos (Python), Investigador Web, Experto en Visualización, Modelador Predictivo.
- Infraestructura: LiteLLM Proxy (`litellm-config.yaml`) y Docker Compose.

### Flujo alto nivel
1) El frontend crea un `sessionId` (UUID).
2) `FileUploader` sube un CSV/Excel a `/api/analytics/upload-dataset` con `session_id`.
3) El backend guarda el archivo en `/app/uploads`, genera resumen con Pandas y lo persiste en la sesión.
4) `ModelSelector` consulta `/api/models/providers` y `/api/models/current?session_id=...` y guarda la selección en `/api/models/configure?session_id=...`.
5) `ChatInterface` envía mensajes a `/api/chat` con `session_id`; el backend invoca `AIManager.run_crew(...)` con el modelo actual.
6) CrewAI coordina agentes usando un `ChatOpenAI` apuntando al proxy de LiteLLM; los agentes ejecutan herramientas y devuelven la respuesta.

### Flujos específicos recientes
- Cambio dinámico de LLM desde la UI:
  - `ModelSelector` llama: `GET /api/models/providers` → muestra `provider/model` disponibles desde LiteLLM.
  - `GET /api/models/current?session_id=...` → muestra modelo activo por sesión.
  - `POST /api/models/configure?session_id=...` con `{ provider, model }` → guarda `session.current_model = "provider/model"`.
  - `chat_routes.py` lee `current_model` de la sesión y lo pasa a `AIManager.run_crew(..., model=current_model)`.

- Modelado predictivo (nuevo agente Modelador Predictivo):
  - El Director de Proyecto delega a "Científico de Datos de Machine Learning" cuando la tarea requiere entrenar o predecir.
  - Herramientas usadas: `ModelTrainingTool` (entrenamiento) y `ModelPredictionTool` (predicción).
  - Entrenamiento: la herramienta recibe `file_path`, `target_column`, `feature_columns` y devuelve (entre otras cosas) una ruta `model_path` persistida; esta ruta debe circular por el `conversation_history`/`context` para futuras predicciones.
  - Predicción: la herramienta recibe `model_path` (del contexto), más `new_data` (desde la tarea), y devuelve resultados.
  - Reglas de contexto en `agents.py`: el `context` debe incluir `file_path:` y, para predicción, también `model_path:`.

### Backend
- `backend/main.py`: configura FastAPI, CORS, rutas `/api/*`, logging y montaje de estáticos.
- Rutas (`backend/api/*`):
  - `chat_routes.py` POST `/api/chat`: recupera sesión, lee `current_model` y orquesta `AIManager`.
  - `analytics_routes.py` POST `/api/analytics/upload-dataset`: guarda fichero, crea contexto de dataset y reinicia historial de conversación.
  - `model_routes.py` GET `/api/models/providers`: lista modelos desde LiteLLM Proxy; POST `/api/models/configure?session_id=...`; GET `/api/models/current?session_id=...`; GET `/api/models/api-keys/status`.
  - `upload_routes.py` POST `/api/upload`: subida genérica a `uploads/` (no usada por el flujo de analytics); GET `/api/upload/list`.
- Gestores (`backend/managers/*`):
  - `global_managers.py`: singletons `ai_manager`, `session_manager`.
  - `session_manager.py`: memoria en proceso de sesiones con `conversation_history`, `file_path`, `dataset_context`.
  - `ai_manager.py`: crea `ChatOpenAI` dinámico por solicitud apuntando a `http://litellm-proxy:4000`, arma agentes de `ProjectAgents` y ejecuta un `Crew` secuencial.
- Agentes (`backend/agents/agents.py`): define equipo y herramientas disponibles (WebSearch, ejecución de código Python, modelado/predicción, visualización).
  - Director: decide a qué especialista delegar; usa "Delegate work to coworker" con `coworker`, `task`, `context`.
  - Analista de Datos: ejecuta Python sobre el dataset con `PythonCodeExecutorTool` (requiere `file_path`).
  - Experto en Visualización: genera código Plotly y lo ejecuta con `CodeExecutionTool` (requiere `file_path`).
  - Modelador Predictivo: entrena y predice vía `ModelTrainingTool`/`ModelPredictionTool` (requiere `file_path` y opcionalmente `model_path`).
- Configuración: `backend/config.py` fija `UPLOADS_DIR=/app/uploads` y asegura su existencia.

### Frontend
- `src/App.jsx`: crea `sessionId`, renderiza `ModelSelector`, `FileUploader` y `ChatInterface` con props.
- `components/ModelSelector.jsx`: usa `modelsApi` para listar y configurar el modelo por sesión.
- `components/FileUploader.jsx`: POST multipart a `/api/analytics/upload-dataset` e incluye `session_id`.
- `services/api.js`: instancia Axios base `/api`; expone `modelsApi`, `chatApi`, etc.

### Integración LiteLLM
- `docker-compose.yml`: servicio `litellm-proxy` (puerto 4000), lee `litellm-config.yaml` y deshabilita telemetría.
- `litellm-config.yaml`:
  - `model_list`: modelos con nombre compuesto `provider/model` (p. ej. `openai/gpt-4o-mini`).
  - `general_settings.master_key`: clave de acceso; se usa como Bearer al consultar `/v1/models`.

### Endpoints clave
- `POST /api/analytics/upload-dataset` (Form: `session_id`, `file`): devuelve `columns`, `shape`, `file_path`, `preview`.
- `GET /api/models/providers`: devuelve `{ providers: [{ name, models: [{name}] }] }` desde LiteLLM.
- `POST /api/models/configure?session_id=...` Body: `{ provider, model }`: guarda `current_model` en sesión.
- `GET /api/models/current?session_id=...`: devuelve `{ provider, model }`.
- `POST /api/chat` Body: `{ session_id, message, ... }`: ejecuta Crew y responde `{ response }`.

### Casos de uso
- Cambio de modelo (LLM) por sesión: seleccionar en `ModelSelector` → guardar → siguientes mensajes de chat usan ese modelo vía LiteLLM.
- Entrenar un modelo predictivo: pedir "entrena un modelo para predecir X con Y" → el Modelador usa `ModelTrainingTool`, devuelve `model_path` y explica la evaluación.
- Predecir con un modelo entrenado: pedir "usa el modelo guardado para predecir ..." → incluirá `model_path` en el contexto y `new_data` en la tarea; devuelve predicciones.

### Seguridad y estado
- Sesiones en memoria (por proceso). Para producción, considerar Redis o base de datos para persistencia/escala.
- Subidas de archivos en volumen `./uploads:/app/uploads` bajo Docker.

### Despliegue y ejecución
- Docker Compose: `docker-compose up --build` (levanta `litellm-proxy` y `crewai-app`). Asegurar variables en `.env` (API keys) y `master_key` consistente con backend.
- Local sin Docker: iniciar LiteLLM por separado o configurar `AIManager` para apuntar a un endpoint local.

### Diagramas (ver también workflow_diagram.html)
Diagramas Mermaid integrados en `workflow_diagram.html` ilustran:
- Diagrama de componentes (Frontend ⇄ Backend ⇄ LiteLLM ⇄ Proveedores).
- Secuencia de carga y chat con sesión y selección de modelo.


