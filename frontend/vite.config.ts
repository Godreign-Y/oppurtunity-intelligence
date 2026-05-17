import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      // Warn above 1MB instead of 500KB — our bundle is expected to be larger
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          // Split heavy deps into separate chunks for better caching
          manualChunks: {
            vendor: ['react', 'react-dom'],
            charts: ['recharts'],
            icons: ['lucide-react'],
          },
        },
      },
    },
    define: {
      // Expose API base URL for axios client in production
      __API_BASE_URL__: JSON.stringify(env.VITE_API_BASE_URL || ''),
    },
  }
})
