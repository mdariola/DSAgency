// En frontend/src/components/ChatInterface.jsx

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Typography, Spin, notification } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import { chatApi } from '../services/api';

const { Text, Paragraph } = Typography;

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
            // Prepara el contexto si hay un archivo cargado
            const requestContext = uploadedFile ? { file_path: uploadedFile.path } : null;

            // Llama a la API usando el sessionId que viene de las props
            const response = await chatApi.sendChatMessage(
                message,
                sessionId,
                modelProvider,
                modelName,
                requestContext
            );

            // Ya no es necesario actualizar el ID de sesión aquí
            
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
            <div style={{ flexGrow: 1, overflowY: 'auto', maxHeight: '400px', marginBottom: '10px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
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
                                <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>
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