import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function POST(req: Request) {
  try {
    const payload = await req.json();
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to connect to backend auth service' }, { status: 500 });
  }
}
