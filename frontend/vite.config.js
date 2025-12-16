import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/weather': 'http://127.0.0.1:8000',
      '/predict': 'http://127.0.0.1:8000',
      '/forecast': 'http://127.0.0.1:8000',
      '/cluster': 'http://127.0.0.1:8000',
    }
  }
})
