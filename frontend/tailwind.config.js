/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        agro: {
          green: '#16a34a',
          dark: '#14532d',
          accent: '#22c55e',
          light: '#f0fdf4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        brand: ['Lexend', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '5xl': '2.5rem',
      },
    },
  },
  plugins: [],
};
