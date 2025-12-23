import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: 'app',
  publicDir: 'static',
  
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'app/templates/index.html')
      }
    }
  }
})
