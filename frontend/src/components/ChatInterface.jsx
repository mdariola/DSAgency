import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Typography, Spin, notification } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import { chatApi } from '../services/api';

const { Text, Paragraph } = Typography;

// ===================================================================================
// === NUEVO COMPONENTE AUXILIAR PARA RENDERIZAR EL CONTENIDO DEL MENSAJE ===
// ===================================================================================
/**
 * Este componente revisa el contenido de un mensaje.
 * Si detecta una ruta a un gráfico HTML, renderiza el gráfico en un iframe.
 * De lo contrario, muestra el texto plano.
 */
const MessageContent = ({ content }) => {
  // Expresión regular para buscar la ruta del gráfico en el texto.
  // Captura rutas como: /charts/chart_d9a35807-7c67-4b97-9c6a-d5df31a30f43.html
  const chartPathRegex = /(\/charts\/[a-zA-Z0-9_-]+\.html)/;
  const match = content.match(chartPathRegex);

  // Si no hay coincidencia, renderiza el texto normalmente.
  if (!match) {
    return <div style={{ whiteSpace: 'pre-line' }}>{content}</div>;
  }

  const chartPath = match[0]; // La ruta completa, ej: /charts/chart_....html
  const precedingText = content.substring(0, match.index); // El texto que el bot escribió antes del enlace

  return (
    <div>
      {/* Muestra cualquier texto introductorio que haya generado el agente */}
      {precedingText && <p style={{ marginBottom: '10px' }}>{precedingText}</p>}
      
      {/* El iframe que renderiza el gráfico HTML */}
      <iframe
        src={chartPath}
        title="Generated Chart"
        style={{ 
          width: '100%', 
          minHeight: '450px', // Puedes ajustar esta altura
          border: '1px solid #f0f0f0', // Un borde sutil para el gráfico
          borderRadius: '8px'
        }}
        // sandbox es un atributo de seguridad importante para iframes
        sandbox="allow-scripts allow-same-origin" 
      />
    </div>
  );
};


// ===================================================================================
// === COMPONENTE PRINCIPAL DEL CHAT (ACTUALIZADO) ===
// ===================================================================================
const ChatInterface = ({ modelProvider, modelName, initialQuestion = null, onChatStart = () => {}, uploadedFile = null, sessionId }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (initialQuestion && !messages.some(msg => msg.type === 'user')) {
            handleSendMessage(initialQuestion);
        }
    }, [initialQuestion]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (messageToSend = null) => {
        const message = messageToSend || inputMessage;
        if (!message.trim()) return;
        if (onChatStart) onChatStart();

        const userMessage = {
            type: 'user',
            content: message,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const requestContext = uploadedFile ? { file_path: uploadedFile.file_path } : null;

            const response = await chatApi.sendChatMessage(
                message,
                sessionId,
                modelProvider,
                modelName,
                requestContext
            );
            
            const aiMessage = {
                type: 'ai',
                content: response.data.response || "No se recibió contenido en la respuesta.",
                timestamp: new Date().toISOString(),
                agentResults: response.data.agent_results
            };
            setMessages(prev => [...prev, aiMessage]);

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                type: 'system',
                content: "I'm having trouble generating a response. Please try again.",
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
            notification.error({
                message: 'Chat Error',
                description: error.response?.data?.detail || error.message || 'Failed to send message',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <Card title="Chat Assistant" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flexGrow: 1, overflowY: 'auto', maxHeight: '500px', marginBottom: '10px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#555', marginTop: '20px' }}>
                        <RobotOutlined style={{ fontSize: '24px' }} />
                        <Paragraph>Ask me about your data science project</Paragraph>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div key={index} style={{ marginBottom: '12px', textAlign: msg.type === 'user' ? 'right' : 'left' }}>
                            <div style={{
                                display: 'inline-block',
                                maxWidth: '80%',
                                padding: '10px',
                                borderRadius: '8px',
                                backgroundColor: msg.type === 'user' ? '#1890ff' : (msg.type === 'system' ? '#ffccc7' : 'white'),
                                color: msg.type === 'user' ? 'white' : 'rgba(0, 0, 0, 0.85)',
                                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                            }}>
                                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                                    {msg.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                                    {' '}
                                    {msg.type === 'user' ? 'You' : (msg.type === 'system' ? 'System' : 'AI Assistant')}
                                </div>
                                
                                {/* APLICAMOS LA LÓGICA DE RENDERIZADO CONDICIONAL AQUÍ */}
                                {msg.type === 'ai' ? (
                                    <MessageContent content={msg.content} />
                                ) : (
                                    <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>
                                )}

                            </div>
                        </div>
                    ))
                )}
                {isLoading && (
                    <div style={{ textAlign: 'center', margin: '10px 0' }}>
                        <Spin size="small" /> <Text type="secondary">Thinking...</Text>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <div style={{ display: 'flex', marginTop: 'auto' }}>
                <Input.TextArea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message here..."
                    autoSize={{ minRows: 1, maxRows: 3 }}
                    disabled={isLoading}
                    style={{ flexGrow: 1 }}
                />
                <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={() => handleSendMessage()}
                    disabled={isLoading || !inputMessage.trim()}
                    style={{ marginLeft: '8px', height: 'auto' }}
                />
            </div>
        </Card>
    );
};

export default ChatInterface;