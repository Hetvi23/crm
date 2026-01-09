import frappeUIPreset from 'frappe-ui/tailwind'

export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
  ],
  safelist: [{ pattern: /!(text|bg)-/, variants: ['hover', 'active'] }],
  theme: {
    extend: {
      colors: {
        'meta-blue': '#1877F2',
        'meta-blue-hover': '#166FE5',
        'meta-gray': '#F0F2F5',
        'meta-gray-light': '#F2F3F5',
        'meta-gray-medium': '#65676B',
        'meta-gray-dark': '#050505',
        'meta-border': '#DADDE1',
        'meta-white': '#FFFFFF',
        'meta-active': '#E7F3FF',
      },
      fontFamily: {
        'meta': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
