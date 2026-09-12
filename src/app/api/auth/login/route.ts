import { NextResponse } from 'next/server';
<<<<<<< HEAD
import { users } from '../../../../lib/mockUsers';

function makeToken(userId: string) {
  return Buffer.from(JSON.stringify({ id: userId, ts: Date.now() })).toString('base64');
}

export async function POST(req: Request) {
  try {
    const { email, password } = await req.json();
    if (!email || !password) return NextResponse.json({ error: 'Missing credentials' }, { status: 400 });

    const user = users.find((u) => u.email.toLowerCase() === email.toLowerCase());
    // For demo accept any password = 'password' or if user exists
    if (!user || password !== 'password') return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });

    const token = makeToken(user.id);
    return NextResponse.json({ token, user });
  } catch (err) {
=======

const API_BASE_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function POST(req: Request) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(await req.json()),
    });
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
>>>>>>> origin/Abhishek
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}
