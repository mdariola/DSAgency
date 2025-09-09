import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  FormLabel,
  Select,
  Button,
  Flex,
  Heading,
  Text,
  useToast,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Divider,
  Input,
  InputGroup,
  InputRightElement,
  IconButton,
  Tooltip,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid
} from '@chakra-ui/react';
import { modelsApi } from '../services/api';
import { InfoIcon, ViewIcon, ViewOffIcon, CheckIcon, WarningIcon } from '@chakra-ui/icons';

const ModelSelector = ({ onModelChange, sessionId }) => {
  const [providers, setProviders] = useState({});
  const [currentProvider, setCurrentProvider] = useState('');
  const [currentModel, setCurrentModel] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(true);
  const [apiKeys, setApiKeys] = useState({});
  const [showApiKey, setShowApiKey] = useState({});
  const [currentApiStatus, setCurrentApiStatus] = useState({});
  const toast = useToast();

  // Descripciones estáticas (pueden quedar igual)
  const modelDescriptions = {
    'openai': {
      description: 'OpenAI models including GPT-4o and GPT-3.5 Turbo',
      website: 'https://openai.com',
      models: {
        'gpt-4o': 'Latest multimodal model with vision and voice capabilities',
        'gpt-4o-mini': 'Smaller, more affordable multimodal model',
        'gpt-4-turbo': 'Powerful and fast GPT-4 variant',
        'gpt-3.5-turbo': 'Cost-effective, general purpose model'
      }
    },
    'anthropic': {
      description: 'Claude models by Anthropic',
      website: 'https://anthropic.com',
      models: { 'claude-3-5-sonnet-20241022': 'Powerful and efficient model' }
    }
    // ...otras descripciones
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const providersResponse = await modelsApi.getProviders();
        
        // --- INICIO DE LA CORRECCIÓN CLAVE ---
        // Transformamos el array de proveedores que llega de la API en un objeto (mapa).
        const providersObject = providersResponse.data.providers.reduce((acc, provider) => {
          acc[provider.name] = {
            ...provider,
            // Nos aseguramos de que 'models' sea una lista de strings (nombres)
            models: provider.models.map(m => m.name)
          };
          return acc;
        }, {});
        setProviders(providersObject);
        // --- FIN DE LA CORRECCIÓN CLAVE ---

        const currentModelResponse = await modelsApi.getCurrentModel(sessionId);
        // Aseguramos que el provider sea un string, ya que la API puede devolver un objeto
        const providerName = typeof currentModelResponse.data.provider === 'object' 
          ? currentModelResponse.data.provider.name 
          : currentModelResponse.data.provider;
        const modelName = currentModelResponse.data.model;
        
        setCurrentProvider(providerName);
        setCurrentModel(modelName);
        
        setSelectedProvider(providerName);
        setSelectedModel(modelName);

        const apiStatusResponse = await modelsApi.getApiKeyStatus();
        setCurrentApiStatus(apiStatusResponse.data);

      } catch (error) {
        console.error('Error fetching model data:', error);
        toast({
          title: 'Error fetching model data',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [sessionId, toast]);

  const handleProviderChange = (e) => {
    const providerName = e.target.value;
    setSelectedProvider(providerName);
    
    if (providers[providerName] && providers[providerName].models.length > 0) {
      setSelectedModel(providers[providerName].models[0]);
    } else {
      setSelectedModel('');
    }
  };

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await modelsApi.configureModel(selectedProvider, selectedModel, sessionId);
      
      setCurrentProvider(selectedProvider);
      setCurrentModel(selectedModel);

      if (onModelChange) {
        onModelChange(selectedProvider, selectedModel);
      }
      
      toast({
        title: 'Model configuration updated',
        description: `Using ${selectedProvider}/${selectedModel}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error saving model configuration:', error);
      toast({
        title: 'Error saving model configuration',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApiKeyChange = (provider, value) => {
    setApiKeys({ ...apiKeys, [provider]: value });
  };

  const toggleApiKeyVisibility = (provider) => {
    setShowApiKey({ ...showApiKey, [provider]: !showApiKey[provider] });
  };

  const saveApiKey = async (provider) => {
    // ... (esta función puede quedar igual)
  };

  // El JSX se renderiza correctamente ahora que `providers` es un objeto
  return (
    <Card mb={4}>
      <CardHeader>
        <Heading size="md">AI Model Configuration</Heading>
      </CardHeader>
      <CardBody>
        <Tabs variant="enclosed">
          <TabList>
            <Tab>Current Model</Tab>
            <Tab>API Keys</Tab>
          </TabList>
          <TabPanels>
            <TabPanel>
              <Box mb={4}>
                <Text fontWeight="bold" mb={2}>Active Configuration:</Text>
                <Flex alignItems="center" mb={2}>
                  <Badge colorScheme="green" mr={2} p={1}>
                    {currentProvider && typeof currentProvider === 'string'
                      ? currentProvider.charAt(0).toUpperCase() + currentProvider.slice(1)
                      : ''}
                  </Badge>
                  <Text>/</Text>
                  <Badge colorScheme="blue" ml={2} p={1}>
                    {currentModel}
                  </Badge>
                </Flex>
                {/* ... (resto del JSX) ... */}
              </Box>
              
              <Divider my={4} />
              
              <Heading size="sm" mb={3}>Change Model</Heading>
              <Flex direction="column" gap={4}>
                <FormControl>
                  <FormLabel>AI Provider</FormLabel>
                  <Select
                    value={selectedProvider}
                    onChange={handleProviderChange}
                    isDisabled={loading || Object.keys(providers).length === 0}
                  >
                    {Object.keys(providers).map((providerName) => (
                      <option key={providerName} value={providerName}>
                        {providerName.charAt(0).toUpperCase() + providerName.slice(1)}
                        {currentApiStatus[providerName] === false && " (API Key Missing)"}
                      </option>
                    ))}
                  </Select>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Model</FormLabel>
                  <Select
                    value={selectedModel}
                    onChange={handleModelChange}
                    isDisabled={loading || !selectedProvider || !providers[selectedProvider]}
                  >
                    {selectedProvider && providers[selectedProvider]?.models.map((modelName) => (
                      <option key={modelName} value={modelName}>
                        {modelName}
                      </option>
                    ))}
                  </Select>
                  {/* ... */}
                </FormControl>
                
                <Button
                  colorScheme="blue"
                  isLoading={loading}
                  onClick={handleSave}
                  isDisabled={
                    loading || 
                    !selectedProvider || 
                    !selectedModel || 
                    (selectedProvider === currentProvider && selectedModel === currentModel) ||
                    currentApiStatus[selectedProvider] === false
                  }
                  mt={2}
                >
                  Save Configuration
                </Button>
                {/* ... */}
              </Flex>
            </TabPanel>
            
            <TabPanel>
              <Accordion allowMultiple>
                {Object.values(providers).map((provider) => (
                  <AccordionItem key={provider.name}>
                    {/* ... (Contenido del AccordionItem) ... */}
                  </AccordionItem>
                ))}
              </Accordion>
            </TabPanel>
          </TabPanels>
        </Tabs>
        
        <Divider my={4} />
        
        <Heading size="sm" mb={3}>Available Models</Heading>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
          {Object.values(providers).map((provider) => (
            <Box 
              key={provider.name} 
              p={3} 
              borderWidth="1px" 
              borderRadius="md" 
              borderColor={provider.name === currentProvider ? "blue.300" : "gray.200"}
              bg={provider.name === currentProvider ? "blue.50" : "white"}
            >
              {/* ... (Contenido del SimpleGrid item) ... */}
            </Box>
          ))}
        </SimpleGrid>
      </CardBody>
    </Card>
  );
};

export default ModelSelector;
