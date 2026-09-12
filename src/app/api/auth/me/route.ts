import { NextResponse } from 'next/server';
<<<<<<< HEAD
import { users } from '../../../../lib/mockUsers';

function parseToken(token?: string) {
  if (!token) return null;
  try {
    const json = Buffer.from(token, 'base64').toString('utf-8');
    return JSON.parse(json);
  } catch (err) {
    return null;
  }
}

export async function GET(req: Request) {
  const url = new URL(req.url);
  const token = url.searchParams.get('token') || req.headers.get('authorization')?.replace('Bearer ', '') || undefined;
  const payload = parseToken(token || undefined);
  if (!payload) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const user = users.find((u) => u.id === payload.id);
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  return NextResponse.json({ user });
=======

const API_BASE_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function GET(req: Request) {
  const authorization = req.headers.get('authorization');
  if (!authorization) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: authorization },
    });
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Authentication service unavailable' }, { status: 503 });
  }
>>>>>>> origin/Abhishek
}
