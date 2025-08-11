import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({

  // Define la carpeta base pública
  base: '/',

  plugins: [react()],

  build: {
    // Define el directorio de salida relativo a la raíz del proyecto
    outDir: path.resolve(__dirname, 'dist'),
    // Asegura que el manifest se genere
    manifest: true,
    rollupOptions: {
      // Define el punto de entrada explícitamente
      input: {
        main: path.resolve(__dirname, 'index.html')
      }
    }
  }
})