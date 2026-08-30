import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vite'
import devtoolsJson from 'vite-plugin-devtools-json'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        // Overridable for e2e tests, which run the backend on a free port
        target: process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  plugins: [react(), devtoolsJson(), tsconfigPaths()],
})
