import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/platform/',
  server: {
    port: 5173,
    proxy: {
      '/api/platform': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
