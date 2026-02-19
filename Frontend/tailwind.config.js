/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          primary: '#16A6AF',
          secondary: '#63536C',
          accent: '#F9953A',
          dark: '#171D24',
        },
        fontFamily: {
          roboto: ['Roboto', 'sans-serif'],
        },
      },
    },
    plugins: [],
  }