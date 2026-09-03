import { NextResponse } from 'next/server';
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
}
