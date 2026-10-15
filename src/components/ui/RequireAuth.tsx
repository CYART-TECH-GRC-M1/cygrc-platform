"use client";
import React, { useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";

export default function RequireAuth({ children, role }: { children: React.ReactNode; role?: string }) {
  const { user, loading, hasRole } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push('/login');
    if (!loading && user && role && !hasRole(role)) router.push('/');
  }, [loading, user, role, hasRole, router]);

  if (loading || !user) return <div className="p-6">Checking access...</div>;
  return <>{children}</>;
}
