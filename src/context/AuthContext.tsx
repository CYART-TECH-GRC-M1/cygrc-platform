"use client";
import React, { createContext, useContext, useEffect, useState } from "react";

type User = { id: string; email: string; name: string; role: string } | null;

type AuthContextType = {
  user: User;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (role: string) => boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem('cygrc_token');
    const u = localStorage.getItem('cygrc_user');
    if (t && u) {
      setToken(t);
      try { setUser(JSON.parse(u)); } catch { setUser(null); }
    }
    setLoading(false);
  }, []);

  async function login(email: string, password: string) {
    setLoading(true);
    const res = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
    const json = await res.json();
    if (!res.ok) { setLoading(false); throw new Error(json?.error || 'Login failed'); }
    setToken(json.token);
    setUser(json.user);
    localStorage.setItem('cygrc_token', json.token);
    localStorage.setItem('cygrc_user', JSON.stringify(json.user));
    setLoading(false);
  }

  async function logout() {
    setLoading(true);
    await fetch('/api/auth/logout', { method: 'POST' });
    localStorage.removeItem('cygrc_token');
    localStorage.removeItem('cygrc_user');
    setToken(null);
    setUser(null);
    setLoading(false);
  }

  function hasRole(role: string) {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return user.role === role;
  }

  return <AuthContext.Provider value={{ user, token, loading, login, logout, hasRole }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
