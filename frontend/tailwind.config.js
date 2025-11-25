/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        racing: {
          red: '#DC2626',
          black: '#0F0F0F',
          gray: '#1F2937',
          silver: '#9CA3AF',
          green: '#059669',
          yellow: '#D97706',
        }
      },
      fontFamily: {
        'racing': ['Orbitron', 'monospace'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
}