import { NextResponse } from 'next/server';
import { risks, Risk } from '../../../../lib/mockRisks';

export async function GET(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const found = risks.find((r) => r.id === id);
  if (!found) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json({ data: found });
}

export async function PUT(req: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const params = await context.params;
    const id = params.id;
    const body = await req.json();
    const idx = risks.findIndex((r) => r.id === id);
    if (idx === -1) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    const updated: Risk = { ...risks[idx], ...body, updatedAt: new Date().toISOString() };
    risks[idx] = updated;
    return NextResponse.json({ data: updated });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}

export async function DELETE(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const idx = risks.findIndex((r) => r.id === id);
  if (idx === -1) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  risks.splice(idx, 1);
  return NextResponse.json({ success: true });
}
