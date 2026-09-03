import { NextResponse } from 'next/server';

export async function POST() {
  // In a real app we'd clear cookies or revoke tokens. For demo, client clears localStorage.
  return NextResponse.json({ success: true });
}
