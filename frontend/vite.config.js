import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['152.png', '512.png'],
      manifest: {
        name: '秋招助手',
        short_name: '秋招助手',
        description: '秋招求职指挥台 - 投递追踪、岗位速递、AI 复盘',
        theme_color: '#2563eb',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: '152.png', sizes: '152x152', type: 'image/png' },
          { src: '512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' }
  }
})
