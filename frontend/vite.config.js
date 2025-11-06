import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1', // `host` 옵션을 `127.0.0.1`로 설정
    hmr: {
      host: '127.0.0.1', // HMR도 같은 값으로 설정
    },
  }
})
