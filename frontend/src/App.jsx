// En frontend/src/App.jsx
import React, { useState, useEffect } from 'react'; // Importa useEffect
import { Divider, Card, Typography } from 'antd';
import ChatInterface from './components/ChatInterface';
import ModelSelector from './components/ModelSelector';
import FileUploader from './components/FileUploader';
import { v4 as uuidv4 } from 'uuid'; // Importa el generador de UUIDs

const { Paragraph } = Typography;

function App() {
  const [modelConfig, setModelConfig] = useState({
    provider: 'openai',
    name: 'gpt-4o-mini'
  });
  const [datasetInfo, setDatasetInfo] = useState(null);
  
  // --- CAMBIO #1: GESTIONAR EL ID DE SESIÓN AQUÍ ---
  const [sessionId, setSessionId] = useState(null);

  // --- CAMBIO #2: GENERAR EL ID CUANDO LA APP CARGA ---
  useEffect(() => {
    // Genera un ID de sesión único cuando el componente se monta por primera vez
    setSessionId(uuidv4()); 
  }, []);


  const handleModelChange = (provider, name) => {
    setModelConfig({ provider, name });
  };

  const handleUploadSuccess = (data) => {
    // La respuesta del backend ahora debería incluir el session_id,
    // pero usamos el que ya generamos para mantener la consistencia.
    console.log("App.jsx: Archivo cargado exitosamente.", data);
    setDatasetInfo(data); // Guardamos toda la data de la respuesta
  };

  return (
    <div className="app-container">
      <h1>DSAgency - AI Assistant Platform</h1>
      <p>Session ID: {sessionId}</p> {/* Opcional: para depurar */}
      
      <ModelSelector onModelChange={handleModelChange} />
      <Divider />

      {/* --- CAMBIO #3: PASAR EL SESSION_ID AL FILEUPLOADER --- */}
      <FileUploader onUploadSuccess={handleUploadSuccess} sessionId={sessionId} />

      {datasetInfo && (
        <Card title="Resumen del Dataset Cargado" style={{marginTop: '16px'}}>
          <Paragraph><strong>Archivo:</strong> {datasetInfo.filename}</Paragraph>
          <Paragraph><strong>Dimensiones:</strong> {datasetInfo.shape[0]} filas, {datasetInfo.shape[1]} columnas</Paragraph>
          <Paragraph><strong>Columnas:</strong> {datasetInfo.columns.join(', ')}</Paragraph>
        </Card>
      )}

      <Divider />

      {/* --- CAMBIO #4: PASAR EL SESSION_ID AL CHAT --- */}
      <ChatInterface
        modelProvider={modelConfig.provider}
        modelName={modelConfig.name}
        uploadedFile={datasetInfo} 
        sessionId={sessionId} // Le pasamos el mismo ID de sesión
      />
    </div>
  );
}

export default App;