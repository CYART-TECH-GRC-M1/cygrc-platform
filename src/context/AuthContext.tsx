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
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
    let res: Response;
    try {
      res = await fetch(`${backendUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
    } catch {
      setLoading(false);
      throw new Error('Network error: Unable to connect to CyGRC backend server. Please verify the backend is running on port 8000.');
    }

    const rawText = await res.text();
    let json: any = {};
    try {
      json = rawText ? JSON.parse(rawText) : {};
    } catch {
      setLoading(false);
      throw new Error(
        res.status === 500
          ? 'Backend server returned 500 Internal Server Error. Please verify the backend service is running on http://127.0.0.1:8000.'
          : `Server returned HTTP ${res.status}: ${rawText || 'Non-JSON response'}`
      );
    }

    if (!res.ok || !json.access_token) {
      setLoading(false);
      throw new Error(json?.detail || json?.error || 'Login failed');
    }

    let meRes: Response;
    try {
      meRes = await fetch(`${backendUrl}/auth/me`, {
        headers: { Authorization: `Bearer ${json.access_token}` },
      });
    } catch {
      setLoading(false);
      throw new Error('Network error loading user profile.');
    }

    const meText = await meRes.text();
    let me: any = {};
    try {
      me = meText ? JSON.parse(meText) : {};
    } catch {
      setLoading(false);
      throw new Error(`Profile service returned HTTP ${meRes.status}: ${meText}`);
    }

    if (!meRes.ok) {
      setLoading(false);
      throw new Error(me?.detail || me?.error || 'Unable to load user profile');
    }

    const authenticatedUser = {
      id: me.user_id,
      email: me.email || email,
      name: [me.first_name, me.last_name].filter(Boolean).join(' ') || me.email || email,
      role: me.role || 'Employee',
    };
    setToken(json.access_token);
    setUser(authenticatedUser);
    localStorage.setItem('cygrc_token', json.access_token);
    localStorage.setItem('cygrc_user', JSON.stringify(authenticatedUser));
    setLoading(false);
  }

  async function logout() {
    setLoading(true);
    localStorage.removeItem('cygrc_token');
    localStorage.removeItem('cygrc_user');
    setToken(null);
    setUser(null);
    setLoading(false);
  }

  function hasRole(role: string) {
    if (!user) return false;
    return user.role.toLowerCase() === role.toLowerCase() || user.role.toLowerCase() === 'admin';
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
