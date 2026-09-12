"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
<<<<<<< HEAD
import { ThemeProvider } from "next-themes";
=======
import { ThemeProvider } from "@/context/ThemeContext";
>>>>>>> origin/Abhishek

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(() => new QueryClient());

  return (
<<<<<<< HEAD
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
    >
=======
    <ThemeProvider>
>>>>>>> origin/Abhishek
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ThemeProvider>
  );
}