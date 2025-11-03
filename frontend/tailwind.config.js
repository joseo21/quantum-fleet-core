/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // 👈 agrega esta línea
  content: ['./public/**/*.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
