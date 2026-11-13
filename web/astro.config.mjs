import { defineConfig } from "astro/config";

// Sitio 100 % estático. Si se publica en una subcarpeta (p. ej. GitHub Pages), define BASE=/motosearch.
export default defineConfig({
  output: "static",
  base: process.env.BASE ?? "/",
  trailingSlash: "always",
});
