
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Fallback logic: use terser if available, else esbuild
function getMinifier() {
  try {
    require.resolve('terser');
    return 'terser';
  } catch (e) {
    return 'esbuild';
  }
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        // Local development API proxy target; configure environment-specific URLs for production builds
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    minify: getMinifier(),
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', '@mui/material'],
          charts: ['chart.js', 'react-chartjs-2']
        }
      }
    }
  }
});
