/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        snow: {
          primary: '#0F4C81',
          secondary: '#62D84E',
          accent: '#FF6B35',
          dark: '#1C1C1C',
          light: '#F5F7FA'
        },
        quality: {
          excellent: '#10B981',
          good: '#3B82F6',
          fair: '#F59E0B',
          poor: '#EF4444'
        },
        dimension: {
          short: '#8B5CF6',
          long: '#3B82F6',
          categorization: '#10B981',
          resolution: '#F59E0B'
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    },
  },
  plugins: [],
}
