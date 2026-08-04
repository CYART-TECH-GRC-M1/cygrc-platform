import { NextResponse } from 'next/server';
import { evidences, Evidence } from '../../../lib/mockEvidence';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') || '';
  const page = parseInt(url.searchParams.get('page') || '1', 10);
  const pageSize = parseInt(url.searchParams.get('pageSize') || '20', 10);

  let filtered = evidences.filter((e) => e.name.toLowerCase().includes(q.toLowerCase()));
  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const items = filtered.slice(start, end).map(({ dataUrl, ...meta }) => meta); // do not include dataUrl in list

  return NextResponse.json({ data: items, total, page, pageSize });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    if (!body || !body.name || !body.dataUrl) return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
    const id = 'e' + Date.now();
    const item: Evidence = {
      id,
      name: body.name,
      type: body.type || 'application/octet-stream',
      size: body.size || 0,
      dataUrl: body.dataUrl,
      createdAt: new Date().toISOString(),
    };
    evidences.unshift(item);
    return NextResponse.json({ data: { id: item.id, name: item.name, type: item.type, size: item.size, createdAt: item.createdAt } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}
