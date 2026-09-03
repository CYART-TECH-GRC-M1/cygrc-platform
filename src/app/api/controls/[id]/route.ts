import { NextResponse } from 'next/server';
import { controls, Control } from '../../../../lib/mockControls';

export async function GET(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const found = controls.find(c => c.id === id);
  if (!found) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json({ data: found });
}

export async function PUT(req: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const params = await context.params;
    const id = params.id;
    const body = await req.json();
    const idx = controls.findIndex(c => c.id === id);
    if (idx === -1) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    controls[idx] = { ...controls[idx], ...body } as Control;
    return NextResponse.json({ data: controls[idx] });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}

export async function DELETE(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const idx = controls.findIndex(c => c.id === id);
  if (idx === -1) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  controls.splice(idx, 1);
  return NextResponse.json({ success: true });
}
