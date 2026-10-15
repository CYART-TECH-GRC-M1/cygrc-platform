"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { ThemeProvider as CustomThemeProvider } from "@/context/ThemeContext";
import { NavigationProvider } from "@/context/NavigationContext";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <CustomThemeProvider>
      <NavigationProvider>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </NavigationProvider>
    </CustomThemeProvider>
  );
}