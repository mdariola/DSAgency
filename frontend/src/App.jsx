// En frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { Divider, Card, Typography } from 'antd';
import ChatInterface from './components/ChatInterface';
import ModelSelector from './components/ModelSelector';
import FileUploader from './components/FileUploader';
import { v4 as uuidv4 } from 'uuid';

const { Paragraph } = Typography;

function App() {
  const [modelConfig, setModelConfig] = useState({
    provider: 'openai',
    name: 'gpt-4o-mini'
  });
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  const handleModelChange = (provider, name) => {
    setModelConfig({ provider, name });
  };

  const handleUploadSuccess = (data) => {
    console.log("App.jsx: Archivo cargado exitosamente.", data);
    setDatasetInfo(data);
  };

  return (
    <div className="app-container">
      <h1>DSAgency - AI Assistant Platform</h1>
      <p>Session ID: {sessionId}</p> {/* Opcional: para depurar */}
      
      {/* --- LA CORRECCIÓN CLAVE ESTÁ AQUÍ --- */}
      {/* Ahora SÍ le pasamos el sessionId al componente que lo necesita */}
      <ModelSelector onModelChange={handleModelChange} sessionId={sessionId} />
      
      <Divider />

      <FileUploader onUploadSuccess={handleUploadSuccess} sessionId={sessionId} />

      {datasetInfo && (
        <Card title="Resumen del Dataset Cargado" style={{marginTop: '16px'}}>
          <Paragraph><strong>Archivo:</strong> {datasetInfo.filename}</Paragraph>
          <Paragraph><strong>Dimensiones:</strong> {datasetInfo.shape[0]} filas, {datasetInfo.shape[1]} columnas</Paragraph>
          <Paragraph><strong>Columnas:</strong> {datasetInfo.columns.join(', ')}</Paragraph>
        </Card>
      )}

      <Divider />

      <ChatInterface
        modelProvider={modelConfig.provider}
        modelName={modelConfig.name}
        uploadedFile={datasetInfo} 
        sessionId={sessionId}
      />
    </div>
  );
}

export default App;
