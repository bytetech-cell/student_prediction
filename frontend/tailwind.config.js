/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'risk-low': '#22c55e', // green-500
        'risk-medium': '#eab308', // yellow-500
        'risk-high': '#ef4444', // red-500
      }
    },
  },
  plugins: [],
}
