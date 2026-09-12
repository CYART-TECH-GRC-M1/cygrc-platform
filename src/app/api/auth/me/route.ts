import { NextResponse } from 'next/server';

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
}
