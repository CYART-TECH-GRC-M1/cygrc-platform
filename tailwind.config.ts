import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],

  darkMode: "class",

  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#7C3AED",
          foreground: "#ffffff",
        },

        cyber: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7e22ce",
          800: "#6b21a8",
          900: "#581c87",
        },
      },

      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },

      borderRadius: {
        xl: "12px",
        "2xl": "16px",
        "3xl": "24px",
      },

      boxShadow: {
        soft:
          "0 2px 8px -2px rgba(0,0,0,0.05), 0 4px 12px -4px rgba(0,0,0,0.05)",

        glass:
          "0 8px 32px 0 rgba(124,58,237,0.10)",

        glow:
          "0 0 40px rgba(124,58,237,0.25)",

        "glow-lg":
          "0 0 80px rgba(124,58,237,0.20)",

        "purple-card":
          "0 20px 60px rgba(124,58,237,0.15)",
      },

      animation: {
        "fade-in": "fadeIn 0.5s ease-out",
        "fade-in-up": "fadeInUp 0.7s ease-out",
        "fade-in-down": "fadeInDown 0.7s ease-out",
        "slide-in": "slideIn 0.5s ease-out",
        "scale-in": "scaleIn 0.5s ease-out",

        float: "float 4s ease-in-out infinite",
        "float-slow": "float 6s ease-in-out infinite",

        "pulse-slow": "pulseSlow 4s ease-in-out infinite",

        "border-glow": "borderGlow 3s ease-in-out infinite",
      },

      keyframes: {
        fadeIn: {
          "0%": {
            opacity: "0",
          },
          "100%": {
            opacity: "1",
          },
        },

        fadeInUp: {
          "0%": {
            opacity: "0",
            transform: "translateY(30px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },

        fadeInDown: {
          "0%": {
            opacity: "0",
            transform: "translateY(-20px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },

        slideIn: {
          "0%": {
            transform: "translateX(-20px)",
            opacity: "0",
          },
          "100%": {
            transform: "translateX(0)",
            opacity: "1",
          },
        },

        scaleIn: {
          "0%": {
            transform: "scale(0.92)",
            opacity: "0",
          },
          "100%": {
            transform: "scale(1)",
            opacity: "1",
          },
        },

        float: {
          "0%, 100%": {
            transform: "translateY(0)",
          },
          "50%": {
            transform: "translateY(-12px)",
          },
        },

        pulseSlow: {
          "0%, 100%": {
            transform: "scale(1)",
            opacity: "0.8",
          },
          "50%": {
            transform: "scale(1.08)",
            opacity: "1",
          },
        },

        borderGlow: {
          "0%, 100%": {
            boxShadow: "0 0 0 rgba(124,58,237,0)",
          },
          "50%": {
            boxShadow: "0 0 25px rgba(124,58,237,0.25)",
          },
        },
      },
    },
  },

  plugins: [],
};

export default config;