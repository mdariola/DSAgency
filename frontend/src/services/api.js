import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints for model providers
export const modelsApi = {
  // ... (sin cambios aquí)
  getProviders: () => api.get('/models/providers'),
  getCurrentModel: () => api.get('/models/current'),
  configureModel: (provider, model) => api.post('/models/configure', { provider, model }),
  getApiKeyStatus: () => api.get('/models/api-keys/status'),
  updateApiKey: (provider, apiKey) => api.post('/models/api-keys/update', { provider, apiKey }),
};

// API endpoints for chat
export const chatApi = {
  /**
   * Envía un mensaje de chat al backend.
   * @param {string} message - El mensaje del usuario.
   * @param {string|null} sessionId - El ID de la sesión actual. // <-- CAMBIO #1: Nombre del parámetro actualizado por claridad
   * @param {string|null} modelProvider - El proveedor del modelo (ej. 'openai').
   * @param {string|null} modelName - El nombre del modelo (ej. 'gpt-4o-mini').
   * @param {object|null} context - Contexto adicional, como la ruta del archivo.
   * @returns {Promise}
   */
  sendChatMessage: (message, sessionId = null, modelProvider = null, modelName = null, context = null) => {
    const payload = {
      message,
      session_id: sessionId, // <-- CAMBIO #2: El nombre de la clave ahora es 'session_id' para coincidir con el backend
      model_provider: modelProvider,
      model_name: modelName,
      context: context,
    };
    console.log('[api.js] Enviando payload a /api/chat:', payload);
    return api.post('/chat', payload);
  },
};

// ... (el resto del archivo no necesita cambios)

// API endpoints for web search
export const searchApi = {
  webSearch: (query, count = 10) => api.get('/search', { params: { q: query, count } }),
};

// API endpoints for file upload
export const uploadApi = {
  uploadFile: (formData) => api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
};

// API endpoints for feedback
export const feedbackApi = {
  submitFeedback: (feedback) => api.post('/feedback', feedback),
};

export default api;