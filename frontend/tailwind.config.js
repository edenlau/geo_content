/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Tocanan brand colors - gold/amber accent with professional slate
        primary: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        tocanan: {
          gold: '#c9a227',
          'gold-light': '#d4b84a',
          'gold-dark': '#9e7d1c',
          slate: '#1e293b',
          'slate-light': '#334155',
        },
        geo: {
          excellent: '#22c55e',
          good: '#84cc16',
          adequate: '#f59e0b',
          poor: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        arabic: ['Noto Sans Arabic', 'Tahoma', 'Arial', 'sans-serif'],
        chinese: ['Noto Sans TC', 'Microsoft JhengHei', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
