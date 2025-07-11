/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'gcp-blue': '#1a73e8',
        'gcp-gray': '#5f6368',
        'gcp-light-gray': '#f8f9fa',
      },
      fontFamily: {
        'google': ['Google Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
