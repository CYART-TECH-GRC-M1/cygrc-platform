import type { Metadata } from "next";
import Link from "next/link";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "../context/AuthContext";
import { ThemeProvider } from "../context/ThemeContext";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "CYGRC Security",
  description: "CYGRC is a cybersecurity dashboard and incident response portal built with Next.js.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`} suppressHydrationWarning>
      <body className="min-h-full bg-slate-950 text-slate-100 transition-colors duration-200">
        <ThemeProvider>
          <div className="min-h-full bg-[var(--background)] text-[var(--foreground)] transition-colors duration-200">
            <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 text-slate-900 backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/85 dark:text-slate-100">
              <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4 sm:px-10">
                <Link href="/" className="text-lg font-semibold uppercase tracking-[0.24em] text-slate-900 transition hover:text-slate-700 dark:text-slate-100 dark:hover:text-white">
                  CYGRC
                </Link>
                <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
                  <Link href="/dashboard" className="transition hover:text-slate-900 dark:hover:text-white">
                    Dashboard
                  </Link>
                  <Link href="/incidents" className="transition hover:text-slate-900 dark:hover:text-white">
                    Incidents
                  </Link>
                  <Link href="/resources" className="transition hover:text-slate-900 dark:hover:text-white">
                    Resources
                  </Link>
                  <Link href="/login" className="rounded-full border border-slate-300 px-4 py-2 transition hover:border-slate-400 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800">
                    Sign in
                  </Link>
                  <Link href="/signup" className="rounded-full bg-slate-900 px-4 py-2 text-white transition hover:bg-slate-700 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-slate-200">
                    Sign up
                  </Link>
                </div>
              </div>
            </header>
            <AuthProvider>
              {children}
            </AuthProvider>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
