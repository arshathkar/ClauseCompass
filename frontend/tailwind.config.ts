import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--color-bg)',
        foreground: 'var(--color-text)',
        muted: 'var(--color-text-muted)',
        brand: 'var(--color-brand)',
        focus: 'var(--color-focus)',
        border: 'var(--color-border)',
        
        badge: {
          high: {
            bg: 'var(--color-badge-high-bg)',
            text: 'var(--color-badge-high-text)'
          },
          medium: {
            bg: 'var(--color-badge-medium-bg)',
            text: 'var(--color-badge-medium-text)'
          },
          low: {
            bg: 'var(--color-badge-low-bg)',
            text: 'var(--color-badge-low-text)'
          },
          info: {
            bg: 'var(--color-badge-info-bg)',
            text: 'var(--color-badge-info-text)'
          }
        }
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
} satisfies Config
