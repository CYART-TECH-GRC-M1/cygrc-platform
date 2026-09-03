"use client";
import React, { createContext, useContext, useEffect, useState } from "react";

type User = { id: string; email: string; name: string; role: string } | null;

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
      try {
        setUser(JSON.parse(u));
      } catch {
        localStorage.removeItem('cygrc_token');
        localStorage.removeItem('cygrc_user');
      }
    }
    setLoading(false);
  }, []);

  async function login(email: string, password: string) {
    setLoading(true);
    const res = await fetch(`${API_BASE_URL}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
    const json = await res.json();
    if (!res.ok || !json.access_token) { setLoading(false); throw new Error(json?.detail || 'Login failed'); }

    const meRes = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${json.access_token}` },
    });
    const me = await meRes.json();
    if (!meRes.ok) { setLoading(false); throw new Error(me?.detail || 'Unable to load user profile'); }

    const authenticatedUser = {
      id: me.user_id,
      email: me.email,
      name: [me.first_name, me.last_name].filter(Boolean).join(' ') || me.email,
      role: me.role,
    };
    setToken(json.access_token);
    setUser(authenticatedUser);
    localStorage.setItem('cygrc_token', json.access_token);
    localStorage.setItem('cygrc_user', JSON.stringify(authenticatedUser));
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
    return user.role.toLowerCase() === role.toLowerCase();
  }

  return <AuthContext.Provider value={{ user, token, loading, login, logout, hasRole }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
