import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  root: "src/ui",
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL ?? "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
        bypass(req) {
          // Don't proxy requests for source files (TypeScript, etc.)
          if (req.url?.match(/\.(ts|tsx|js|jsx|map)$/)) {
            return req.url;
          }
        },
      },
    },
  },
  build: {
    outDir: "../../dist",
    emptyOutDir: true,
  },
});
