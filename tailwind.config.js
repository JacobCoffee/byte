/** @type {import('tailwindcss').Config} */
const defaultTheme = require("tailwindcss/defaultTheme")

module.exports = {
  darkMode: "class",
  content: ["./src/server/domain/web/**/*.{html,js,ts,jsx,tsx,j2,jinja2}"],
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
    require("daisyui"),
  ],
  theme: {
    extend: {
      colors: {
        "byte-teal": "#42b1a8",
        "byte-blue": "#7bcebc",
        "byte-light-blue": "#abe6d2",
        "byte-orange": "#d4a35a",
        "byte-red": "#fc7054",
        "byte-dark": "#0c0c0c",
        "byte-white": "#ebebe9",
      },
    },
  },
  daisyui: {
    themes: [
      {
        byte_light: {
          primary: "#42b1a8",
          secondary: "#7bcebc",
          accent: "#abe6d2",
          neutral: "#0c0c0c",
          "base-100": "#ebebe9",
          info: "#6ee7b7",
          success: "#059669",
          warning: "#d4a35a",
          error: "#fc7054",
        },
      },
    ],
  },
}
