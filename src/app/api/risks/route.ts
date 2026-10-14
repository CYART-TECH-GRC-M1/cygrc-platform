import { NextResponse } from 'next/server';
import { risks, Risk } from '../../../lib/mockRisks';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') || '';
  const level = url.searchParams.get('level') || '';
  const status = url.searchParams.get('status') || '';
  const page = parseInt(url.searchParams.get('page') || '1', 10);
  const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);

  let filtered = risks.filter((r) => r.title.toLowerCase().includes(q.toLowerCase()) || (r.description || '').toLowerCase().includes(q.toLowerCase()));
  if (level) filtered = filtered.filter((r) => r.level === level);
  if (status) filtered = filtered.filter((r) => r.status === status);

  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const items = filtered.slice(start, end);

  return NextResponse.json({ data: items, total, page, pageSize });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const id = 'r' + Date.now();
    const item: Risk = {
      id,
      title: body.title || 'Untitled risk',
      description: body.description || '',
      level: body.level || 'Low',
      owner: body.owner || null,
      status: body.status || 'Open',
      createdAt: new Date().toISOString(),
      updatedAt: null,
    };
    risks.unshift(item);
    return NextResponse.json({ data: item }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}
