/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        // Deep dark base palette (charcoal → near-black)
        dark: {
          50: '#E5E7EB',   // primary text
          100: '#D1D5DB',
          200: '#9CA3AF',   // secondary text
          300: '#6B7280',   // muted
          400: '#4B5563',
          500: '#374151',
          600: '#1F2937',
          700: '#151A22',   // card surface
          800: '#111318',   // elevated surface
          900: '#0D0F13',   // sidebar
          950: '#0B0D11',   // deepest base
        },
        // Primary — electric indigo/violet
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        // Surface aliases
        surface: {
          50: '#E5E7EB',
          100: '#D1D5DB',
          200: '#9CA3AF',
          300: '#6B7280',
          400: '#4B5563',
          500: '#374151',
          600: '#1F2937',
          700: '#171B22',
          800: '#12151B',
          900: '#0D0F13',
          950: '#0B0D11',
        },
      },
      boxShadow: {
        // Depth layers — subtle, not heavy
        'depth-sm': '0 1px 2px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.15)',
        'depth-md': '0 4px 6px rgba(0, 0, 0, 0.25), 0 2px 4px rgba(0, 0, 0, 0.15)',
        'depth-lg': '0 10px 20px rgba(0, 0, 0, 0.3), 0 6px 6px rgba(0, 0, 0, 0.15)',
        'depth-xl': '0 20px 40px rgba(0, 0, 0, 0.35), 0 12px 12px rgba(0, 0, 0, 0.15)',
        // Inner depth
        'inner-sm': 'inset 0 1px 3px rgba(0, 0, 0, 0.3)',
        'inner-md': 'inset 0 2px 6px rgba(0, 0, 0, 0.35)',
        // Glow accents
        'glow-primary': '0 0 20px rgba(99, 102, 241, 0.15), 0 0 50px rgba(99, 102, 241, 0.06)',
        'glow-primary-strong': '0 0 20px rgba(99, 102, 241, 0.25), 0 0 60px rgba(99, 102, 241, 0.1)',
        'glow-emerald': '0 0 12px rgba(52, 211, 153, 0.15)',
        'glow-rose': '0 0 12px rgba(251, 113, 133, 0.15)',
      },
      animation: {
        'gradient-x': 'gradient-x 4s ease infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(99, 102, 241, 0.25)' },
        },
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
}
