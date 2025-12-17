/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Добавим наши фирменные цвета сразу
        primary: "#10B981", // Emerald 500
        secondary: "#8B5CF6", // Violet 500
        dark: "#020617", // Slate 950
      }
    },
  },
  plugins: [],
}
