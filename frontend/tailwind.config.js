export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        "risk-low": "#22c55e",
        "risk-medium": "#f59e0b",
        "risk-high": "#ef4444",
        "risk-critical": "#ff0000",
        surface: "#111111",
        base: "#0a0a0a",
      },
      fontFamily: {
        sans: ['"Nexa Serif"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', '"Consolas"', 'monospace'],
      },
    },
  },
  plugins: [],
};
