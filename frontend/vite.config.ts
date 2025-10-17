import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vite'
import devtoolsJson from 'vite-plugin-devtools-json'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), devtoolsJson(), tsconfigPaths()],
})
