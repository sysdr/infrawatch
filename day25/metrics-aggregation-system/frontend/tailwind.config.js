/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'wp-blue': '#0073aa',
        'wp-dark': '#23282d',
        'wp-gray': '#a0a5aa',
      },
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      boxShadow: {
        'wp': '0 1px 3px rgba(0,0,0,0.13)',
        'wp-lg': '0 5px 15px rgba(0,0,0,0.08)',
      }
    },
  },
  plugins: [],
}
