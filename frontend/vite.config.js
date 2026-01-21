import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api/models': {
        target: 'http://127.0.0.1:8013',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://192.168.208.146:8009',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
