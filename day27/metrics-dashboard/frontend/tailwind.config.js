/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'wp-blue': '#0073aa',
        'wp-blue-light': '#00a0d2',
        'wp-admin-bar': '#23282d',
        'wp-gray': '#8c8f94',
        'wp-gray-light': '#f1f1f1'
      }
    },
  },
  plugins: [],
}
