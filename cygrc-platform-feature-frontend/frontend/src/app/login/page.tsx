"use client";
import LoginForm from "./LoginForm";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) router.push('/dashboard');
  }, [user, router]);

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12 sm:px-10 lg:px-12">
      <div className="w-full max-w-3xl">
        <div className="mx-auto grid grid-cols-1 gap-8 md:grid-cols-2">
          <div className="hidden rounded-[1rem] border border-slate-800 bg-slate-900/80 p-8 md:block">
            <h2 className="text-2xl font-semibold text-white">Welcome back</h2>
            <p className="mt-4 text-slate-300">Sign in to access your security dashboard and incident tools.</p>
          </div>
          <div className="rounded-[1.25rem] border border-slate-800 bg-slate-950/95 p-8 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.55)]">
            <LoginForm />
          </div>
        </div>
      </div>
    </main>
  );
}
