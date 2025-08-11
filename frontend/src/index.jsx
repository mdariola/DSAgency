import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider } from '@chakra-ui/react'; // <-- 1. Importamos el proveedor
import App from './App';
import './assets/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ChakraProvider> {/* <-- 2. Envolvemos la App */}
      <App />
    </ChakraProvider>
  </React.StrictMode>
);
