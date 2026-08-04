"use client";
import React, { useState } from "react";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import Link from "next/link";
import Logo from "../../components/Logo";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";

type FormState = {
  email: string;
  password: string;
  remember: boolean;
};

export default function LoginForm() {
  const [form, setForm] = useState<FormState>({ email: "", password: "", remember: false });
  const [show, setShow] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function validate() {
    if (!form.email) return "Email is required";
    if (!form.password) return "Password is required";
    return null;
  }

  const { login } = useAuth();
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const v = validate();
    if (v) return setError(v);
    setLoading(true);
    try {
      await login(form.email, form.password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err?.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="mb-6 flex items-center gap-4">
        <Logo />
        <div>
          <h3 className="text-lg font-semibold text-white">CYGRC</h3>
          <p className="text-sm text-slate-400">Sign in to your account</p>
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          label="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm((s) => ({ ...s, email: e.target.value }))}
        />

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">Password</label>
          <div className="relative">
            <input
              type={show ? "text" : "password"}
              value={form.password}
              onChange={(e) => setForm((s) => ({ ...s, password: e.target.value }))}
              className="mt-1 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50"
            />
            <button
              type="button"
              onClick={() => setShow((s) => !s)}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full px-2 py-1 text-sm text-slate-300 hover:bg-slate-800"
            >
              {show ? "Hide" : "Show"}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <label className="inline-flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={form.remember}
              onChange={(e) => setForm((s) => ({ ...s, remember: e.target.checked }))}
              className="rounded border-slate-700 bg-slate-900 text-slate-100"
            />
            Remember me
          </label>
          <Link href="/forgot" className="text-sm text-slate-200 hover:underline">
            Forgot password?
          </Link>
        </div>

        {error && <p className="text-sm text-rose-400">{error}</p>}

        <div>
          <Button type="submit" loading={loading}>
            Sign in
          </Button>
        </div>
      </form>
    </div>
  );
}
