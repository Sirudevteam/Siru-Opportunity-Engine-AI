import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#070b16",
        paper: "#fbfbff",
        panel: "#ffffff",
        line: "#e6e8ef",
        teal: "#062bff",
        amber: "#d97706",
        coral: "#dc2626",
        blue: "#062bff",
        lavender: "#dfe3ff",
        mint: "#e8f8ee",
        success: "#10885f"
      },
      fontFamily: {
        sans: ["var(--font-raleway)", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        panel: "0 8px 22px rgba(15, 23, 42, 0.045)"
      }
    }
  },
  plugins: []
};

export default config;
