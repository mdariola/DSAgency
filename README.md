# DSAgency - AI Assistant Platform

Una plataforma full-stack para análisis de datos asistido por IA que combina múltiples agentes especializados con capacidades de machine learning, visualización y búsqueda web.

## 🚀 Características Principales

- **Agentes Especializados**: Sistema multi-agente con roles específicos para análisis de datos, visualización, machine learning y búsqueda web
- **Selección Dinámica de Modelos**: Cambio en tiempo real entre diferentes proveedores de LLM (OpenAI, Anthropic) vía LiteLLM Proxy
- **Análisis de Datos Avanzado**: Procesamiento de archivos CSV/Excel con análisis estadístico y visualizaciones interactivas
- **Machine Learning**: Entrenamiento y predicción con modelos de regresión usando scikit-learn
- **Visualizaciones Interactivas**: Generación automática de gráficos con Plotly
- **Búsqueda Web Contextual**: Investigación web con contexto temporal para información actualizada
- **Interfaz Moderna**: Frontend React con Ant Design y Chakra UI

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  LiteLLM Proxy  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Modelos)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Agentes CrewAI │
                       │  + Herramientas │
                       └─────────────────┘
```

### Stack Tecnológico

**Frontend:**
- React 18.3.1
- Ant Design 5.11.0
- Chakra UI 2.10.9
- Axios para comunicación con API
- Vite como bundler

**Backend:**
- FastAPI 0.104.1
- CrewAI 0.157.0 (Framework de agentes)
- LangChain 0.3.27
- Pandas, NumPy, Scikit-learn
- Plotly para visualizaciones

**Infraestructura:**
- Docker & Docker Compose
- LiteLLM Proxy para gestión de modelos
- Uvicorn como servidor ASGI

## 🤖 Agentes del Sistema

### 1. Director de Proyecto
- **Rol**: Coordinador principal que interpreta solicitudes y delega tareas
- **Responsabilidades**: Análisis de peticiones, delegación inteligente a especialistas
- **Herramientas**: Sistema de delegación interno

### 2. Experto Analista de Datos
- **Rol**: Especialista en análisis estadístico y exploración de datos
- **Responsabilidades**: EDA, cálculos estadísticos, resúmenes de datos
- **Herramientas**: `PythonCodeExecutorTool` para ejecución de código Python

### 3. Investigador Web
- **Rol**: Búsqueda de información actualizada en internet
- **Responsabilidades**: Verificación de hechos, información contextual con fecha actual
- **Herramientas**: `WebSearchTool` con API de Serper

### 4. Experto en Visualización
- **Rol**: Creación de gráficos y visualizaciones interactivas
- **Responsabilidades**: Generación de código Plotly, visualizaciones personalizadas
- **Herramientas**: `CodeExecutionTool` para gráficos

### 5. Científico de Datos de ML
- **Rol**: Entrenamiento y predicción con modelos de machine learning
- **Responsabilidades**: Modelos de regresión, predicciones, evaluación de rendimiento
- **Herramientas**: `ModelTrainingTool`, `ModelPredictionTool`

## 🛠️ Herramientas Disponibles

### Análisis de Datos
- **PythonCodeExecutorTool**: Ejecución segura de código Python sobre DataFrames
- **DspyAnalysisTool**: Análisis avanzado usando DSPy framework

### Visualización
- **CodeExecutionTool**: Generación de gráficos interactivos con Plotly
- Soporte para múltiples tipos de gráficos (barras, líneas, scatter, etc.)

### Machine Learning
- **ModelTrainingTool**: Entrenamiento de modelos de regresión lineal
- **ModelPredictionTool**: Predicciones con modelos entrenados
- Persistencia de modelos con joblib

### Búsqueda Web
- **WebSearchTool**: Búsqueda contextual con validación temporal
- Integración con API de Serper para resultados de Google

## 📡 API Endpoints

### Chat y Análisis
- `POST /api/chat` - Procesamiento de mensajes con agentes
- `POST /api/analytics/upload-dataset` - Carga de archivos CSV/Excel

### Gestión de Modelos
- `GET /api/models/providers` - Lista de proveedores disponibles
- `GET /api/models/current` - Modelo actual de la sesión
- `POST /api/models/configure` - Configuración de modelo por sesión
- `GET /api/models/api-keys/status` - Estado de claves API

### Archivos
- `POST /api/upload` - Carga genérica de archivos
- `GET /api/upload/list` - Lista de archivos subidos

### Feedback
- `POST /api/feedback` - Sistema de retroalimentación de usuarios

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

### Configuración de Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# API Keys para proveedores de LLM
OPENAI_API_KEY=tu_clave_openai
ANTHROPIC_API_KEY=tu_clave_anthropic

# API Key para búsqueda web
SERPER_API_KEY=tu_clave_serper

# Configuración de LiteLLM
LITELLM_MASTER_KEY=super-secreto-1234
```

### Instalación con Docker

```bash
# Clonar el repositorio
git clone <repository-url>
cd dsagency

# Construir y ejecutar con Docker Compose
docker-compose up --build
```

El sistema estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- LiteLLM Proxy: http://localhost:4000

### Instalación para Desarrollo

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 Flujo de Trabajo

### 1. Configuración Inicial
1. El usuario accede a la aplicación
2. Se genera automáticamente un `sessionId` único
3. Se configura el modelo de IA preferido

### 2. Carga de Datos
1. Usuario sube archivo CSV/Excel
2. Sistema genera resumen estadístico automático
3. Archivo se almacena con ruta única
4. Contexto se actualiza en la sesión

### 3. Análisis y Chat
1. Usuario envía pregunta o solicitud
2. Director de Proyecto analiza y delega a especialista
3. Agente especializado ejecuta herramientas necesarias
4. Resultado se devuelve al usuario
5. Historial de conversación se mantiene

### 4. Visualizaciones
1. Usuario solicita gráfico
2. Experto en Visualización genera código Plotly
3. Gráfico se ejecuta y guarda como HTML
4. Se muestra en iframe dentro del chat

### 5. Machine Learning
1. Usuario solicita entrenamiento de modelo
2. Científico de Datos entrena modelo con scikit-learn
3. Modelo se guarda con ID único
4. Para predicciones, se recupera modelo del contexto

## 🔧 Configuración Avanzada

### LiteLLM Proxy
El archivo `litellm-config.yaml` define los modelos disponibles:

```yaml
model_list:
  - model_name: openai/gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

general_settings:
  master_key: "super-secreto-1234"
```

### Gestión de Sesiones
- Sesiones se almacenan en memoria (desarrollo)
- Para producción, considerar Redis o base de datos
- Cada sesión mantiene: historial, contexto de archivo, modelo actual

### Personalización de Agentes
Los agentes se pueden personalizar en `backend/agents/agents.py`:
- Modificar roles y responsabilidades
- Ajustar herramientas disponibles
- Personalizar prompts y comportamientos

## 🧪 Casos de Uso

### Análisis Exploratorio
```
Usuario: "Analiza las primeras 10 filas de mi dataset"
→ Director delega a Analista de Datos
→ Ejecuta código Python para mostrar datos
```

### Visualización
```
Usuario: "Crea un gráfico de barras de ventas por región"
→ Director delega a Experto en Visualización
→ Genera código Plotly y muestra gráfico interactivo
```

### Machine Learning
```
Usuario: "Entrena un modelo para predecir precios usando área y habitaciones"
→ Director delega a Científico de Datos
→ Entrena modelo de regresión y muestra métricas
```

### Predicción
```
Usuario: "Usa el modelo para predecir el precio de una casa de 2000m² con 3 habitaciones"
→ Director delega a Científico de Datos
→ Recupera modelo del contexto y hace predicción
```

### Investigación Web
```
Usuario: "¿Cuál es la población actual de México?"
→ Director delega a Investigador Web
→ Busca información actualizada con contexto temporal
```

## 🔒 Seguridad

- Validación de tipos de archivo (solo CSV/Excel)
- Sanitización de rutas de archivos
- Gestión segura de API keys
- Sandbox para ejecución de código Python
- Validación de entrada en todos los endpoints

## 📈 Monitoreo y Logs

- Logs estructurados con timestamps
- Tracking de uso de modelos
- Métricas de rendimiento de agentes
- Sistema de feedback de usuarios

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para reportar bugs o solicitar funcionalidades:
1. Crear issue en GitHub
2. Incluir logs relevantes
3. Describir pasos para reproducir


