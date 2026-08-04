"use client";

import LoginForm from "./LoginForm";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) router.push("/dashboard");
  }, [user, router]);

  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-950">

      {/* Background Glow */}
      <div className="absolute -left-32 top-0 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl"></div>
      <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl"></div>

      <div className="relative z-10 flex min-h-screen items-center justify-center px-6 py-10">

        <div className="grid w-full max-w-6xl overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/60 shadow-2xl backdrop-blur-xl md:grid-cols-2">

          {/* Left Side */}
          <div className="hidden flex-col justify-center bg-gradient-to-br from-blue-700 via-slate-900 to-slate-950 p-12 text-white md:flex">

            <span className="mb-4 inline-block w-fit rounded-full bg-white/10 px-4 py-1 text-sm">
              Enterprise GRC Platform
            </span>

            <h1 className="text-5xl font-bold leading-tight">
              Secure.<br />
              Govern.<br />
              Comply.
            </h1>

            <p className="mt-6 text-lg text-slate-300">
              Manage Audits, Risks, Controls and Compliance from one secure
              dashboard.
            </p>

            <div className="mt-12 grid grid-cols-2 gap-5">

              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-3xl font-bold text-cyan-400">99.9%</p>
                <p className="mt-2 text-slate-300">System Availability</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-3xl font-bold text-emerald-400">500+</p>
                <p className="mt-2 text-slate-300">Audits Completed</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-3xl font-bold text-orange-400">120</p>
                <p className="mt-2 text-slate-300">Active Risks</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-3xl font-bold text-pink-400">ISO</p>
                <p className="mt-2 text-slate-300">Compliance Ready</p>
              </div>

            </div>

          </div>

          {/* Right Side */}
          <div className="flex items-center justify-center bg-slate-950/80 p-10">

            <div className="w-full max-w-md">

              <LoginForm />

            </div>

          </div>

        </div>

      </div>

    </main>
  );
}