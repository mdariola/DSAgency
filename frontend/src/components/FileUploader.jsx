// En frontend/src/components/FileUploader.jsx
import React, { useState } from 'react';
import { Upload, Button, message, Card } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios';

// --- CAMBIO #1: ACEPTAR 'sessionId' COMO PROP ---
const FileUploader = ({ onUploadSuccess, sessionId }) => { 
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    const formData = new FormData();
    fileList.forEach(file => {
      formData.append('file', file);
    });

    // --- CAMBIO #2: ¡LA LÍNEA MÁGICA! ---
    // Añadimos el session_id al formulario antes de enviarlo.
    // Asegúrate de que sessionId no sea null.
    if (sessionId) {
      formData.append('session_id', sessionId);
    } else {
      message.error("Error: No se ha generado un ID de sesión.");
      return;
    }

    setUploading(true);

    try {
      const response = await axios.post('/api/analytics/upload-dataset', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploading(false);
      message.success(`${fileList[0].name} file uploaded successfully.`);
      onUploadSuccess(response.data);
      setFileList([]);

    } catch (error) {
      setUploading(false);
      message.error(`${fileList.length > 0 ? fileList[0].name : 'File'} upload failed.`);
      console.error("Upload error:", error.response ? error.response.data : error);
    }
  };

  const props = {
    onRemove: file => {
      setFileList(prevList => {
        const index = prevList.indexOf(file);
        const newFileList = prevList.slice();
        newFileList.splice(index, 1);
        return newFileList;
      });
    },
    beforeUpload: file => {
      setFileList([file]);
      return false;
    },
    fileList,
  };

  return (
    <Card title="Cargar Archivo para Análisis">
      <Upload {...props}>
        <Button icon={<UploadOutlined />}>Seleccionar Archivo (CSV o Excel)</Button>
      </Upload>
      <Button
        type="primary"
        onClick={handleUpload}
        disabled={fileList.length === 0 || !sessionId} // Deshabilitar si no hay ID de sesión
        loading={uploading}
        style={{ marginTop: 16 }}
      >
        {uploading ? 'Subiendo...' : 'Iniciar Carga'}
      </Button>
    </Card>
  );
};

export default FileUploader;