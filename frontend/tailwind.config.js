/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        leaf: {
          DEFAULT: '#16a34a',
          dark: '#15803d',
          light: '#dcfce7',
        },
        wheat: '#d97706',
        cream: '#f6f8f2',
        ink: '#1c2b1f',
      },
      boxShadow: {
        soft: '0 20px 45px rgba(28, 43, 31, 0.08)',
      },
    },
  },
  plugins: [],
};

