import axios from 'axios';

// Creamos una instancia de axios pre-configurada. Esto está perfecto.
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- SECCIÓN CORREGIDA ---
export const modelsApi = {
  getProviders: () => api.get('/models/providers'),

  // CORRECCIÓN 1: La función ahora acepta 'sessionId'
  getCurrentModel: (sessionId) => {
    // Y lo usa para construir la URL con parámetros de query:
    // /api/models/current?session_id=xxxxxxxx
    return api.get('/models/current', {
      params: { session_id: sessionId }
    });
  },

  // CORRECCIÓN 2: La función ahora acepta 'sessionId'
  configureModel: (provider, model, sessionId) => {
    // El cuerpo de la petición sigue siendo el mismo
    const body = { provider, model };
    // Pero ahora añadimos el sessionId como parámetro de query
    return api.post('/models/configure', body, {
      params: { session_id: sessionId }
    });
  },

  getApiKeyStatus: () => api.get('/models/api-keys/status'),
  
  updateApiKey: (provider, apiKey) => api.post('/models/api-keys/update', { provider, apiKey }),
};

// --- EL RESTO DEL ARCHIVO PUEDE QUEDAR IGUAL ---

export const chatApi = {
  sendChatMessage: (message, sessionId = null, modelProvider = null, modelName = null, context = null) => {
    const payload = {
      message,
      session_id: sessionId,
      model_provider: modelProvider,
      model_name: modelName,
      context: context,
    };
    console.log('[api.js] Enviando payload a /api/chat:', payload);
    return api.post('/chat', payload);
  },
};

export const searchApi = {
  webSearch: (query, count = 10) => api.get('/search', { params: { q: query, count } }),
};

export const uploadApi = {
  uploadFile: (formData) => api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
};

export const feedbackApi = {
  submitFeedback: (feedback) => api.post('/feedback', feedback),
};

export default api;
