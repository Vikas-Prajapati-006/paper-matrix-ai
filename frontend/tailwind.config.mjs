/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        background: '#09090b', // Deep zinc-950
        surface: {
          DEFAULT: '#121215',
          elevated: '#18181b',
          border: '#27272a'
        },
        brand: {
          50: '#f5f3ff',
          100: '#ede9fe',
          500: '#6366f1', // Crisp indigo accent
          600: '#4f46e5',
          700: '#4338ca'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
};