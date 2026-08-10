import { NextResponse } from 'next/server';
import { evidences } from '../../../../lib/mockEvidence';

export async function GET(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const found = evidences.find((e) => e.id === id);
  if (!found) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json({ data: found });
}

export async function DELETE(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const idx = evidences.findIndex((e) => e.id === id);
  if (idx === -1) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  evidences.splice(idx, 1);
  return NextResponse.json({ success: true });
}
