"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
} from "react";

type ThemeMode = "dark";

type ThemeContextType = {
  theme: ThemeMode;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextType | undefined>(
  undefined
);

export function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const theme: ThemeMode = "dark";

  useEffect(() => {
    const root = document.documentElement;

    // Force CYGRC dark theme
    root.classList.remove("light");
    root.classList.add("dark");

    root.style.colorScheme = "dark";

    // Prevent old saved light theme from affecting the app
    window.localStorage.setItem("cygrc-theme", "dark");
  }, []);

  const value = useMemo(
    () => ({
      theme,
      // Single fixed theme — no light/dark switching
      toggleTheme: () => {},
    }),
    []
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);

  if (!ctx) {
    throw new Error(
      "useTheme must be used within ThemeProvider"
    );
  }

  return ctx;
}