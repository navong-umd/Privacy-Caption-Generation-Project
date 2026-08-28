import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: {
    port: 5173,
    // Proxy the API in dev so the app can call /api without CORS friction.
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
      // So the "API" link (Swagger UI) works behind the dev server too.
      "/docs": { target: process.env.VITE_API_PROXY_TARGET || "http://localhost:8000", changeOrigin: true },
      "/openapi.json": { target: process.env.VITE_API_PROXY_TARGET || "http://localhost:8000", changeOrigin: true },
    },
  },
  build: {
    target: "es2020",
    sourcemap: false,
  },
});
