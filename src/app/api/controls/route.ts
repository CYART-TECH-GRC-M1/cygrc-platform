import { NextResponse } from 'next/server';
import { controls, Control } from '../../../lib/mockControls';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') || '';
  const framework = url.searchParams.get('framework') || '';
  const status = url.searchParams.get('status') || '';

  let filtered = controls.filter(c => c.title.toLowerCase().includes(q.toLowerCase()) || (c.description||'').toLowerCase().includes(q.toLowerCase()));
  if (framework) filtered = filtered.filter(c => c.framework === framework);
  if (status) filtered = filtered.filter(c => c.status === status);

  return NextResponse.json({ data: filtered });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const id = 'c' + Date.now();
    const item: Control = {
      id,
      title: body.title || 'Untitled control',
      description: body.description || '',
      framework: body.framework || 'NIST',
      status: body.status || 'Planned',
      owner: body.owner || null,
      evidenceCount: body.evidenceCount || 0,
      createdAt: new Date().toISOString(),
    };
    controls.unshift(item);
    return NextResponse.json({ data: item }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}
