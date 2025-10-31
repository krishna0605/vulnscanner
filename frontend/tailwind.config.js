/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#0ea5e9", // Luminous Sky Blue
        "primary-faint": "rgba(14, 165, 233, 0.5)",
        "background-dark": "#020617", // Deeper Navy
        "surface-dark": "rgba(3, 7, 18, 0.8)", // Semi-transparent near-black
        "text-light": "#e2e8f0", // Light Slate
        "text-dark": "#64748b", // Slate for text
        "border-dark": "rgba(51, 65, 85, 0.5)",
      },
      fontFamily: {
        "sans": ["Roboto", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.375rem", 
        "lg": "0.5rem", 
        "xl": "0.75rem", 
        "full": "9999px"
      },
      boxShadow: {
        'glow': '0 0 15px var(--color-primary-faint)',
      },
      keyframes: {
        'subtle-pan': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        'light-trail': {
          '0%': { backgroundPosition: '-100% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'subtle-pan': 'subtle-pan 25s linear infinite',
        'light-trail': 'light-trail 1.2s linear infinite',
      },
    },
  },
  // Safelist a broad set of utility patterns to avoid JIT misses during cleanup
  safelist: [
    { pattern: /^(container|flex|grid|block|hidden)$/ },
    { pattern: /^(items|justify|content|place)-(start|center|end|between)$/ },
    { pattern: /^(p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml)-[0-9]+$/ },
    { pattern: /^(w|h|min-w|min-h|max-w|max-h)-.+$/ },
    { pattern: /^(text|bg|border|outline|ring|shadow)-.+$/ },
    { pattern: /^(rounded|opacity|translate|scale|skew|animate)-.+$/ },
    // Removed variant safelist pattern that produced warnings; Tailwind
    // automatically picks up variant classes from content scanning.
  ],
  plugins: [require('@tailwindcss/forms')],
};