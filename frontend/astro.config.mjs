import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://paper-matrix-ai.pages.dev',
  integrations: [tailwind()],
  server: {
    port: 4321,
    host: true
  }
});