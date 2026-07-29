import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: (content, filename) => {
          if (filename && filename.replace(/\\/g, '/').includes('variables.scss')) {
            return content
          }
          return `@use "@/assets/styles/variables.scss" as *;${content}`
        }
      }
    }
  }
})
