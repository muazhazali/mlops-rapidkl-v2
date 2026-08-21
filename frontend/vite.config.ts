import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/forecast': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/predict': 'http://localhost:8000',
    },
  },
  build: {
    outDir: '../api/static',
    emptyOutDir: true,
  },
})