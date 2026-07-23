import { NextResponse } from 'next/server';

type Audit = {
  id: string;
  title: string;
  description: string;
  status: 'Open' | 'In Progress' | 'Completed';
  auditor?: string | null;
  dueDate?: string | null;
  createdAt: string;
};

let audits: Audit[] = [
  {
    id: '1',
    title: 'Quarterly SOC Audit',
    description: 'Review SOC controls and incident handling.',
    status: 'Open',
    auditor: null,
    dueDate: '2026-08-15',
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'PCI Compliance Assessment',
    description: 'Validate PCI scope and controls.',
    status: 'In Progress',
    auditor: 'alice@corp.com',
    dueDate: '2026-09-01',
    createdAt: new Date().toISOString(),
  },
  {
    id: '3',
    title: 'Vulnerability Management Audit',
    description: 'Assess patching and vulnerability remediation.',
    status: 'Completed',
    auditor: 'bob@corp.com',
    dueDate: '2026-06-30',
    createdAt: new Date().toISOString(),
  },
];

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') || '';
  const status = url.searchParams.get('status') || '';
  const page = parseInt(url.searchParams.get('page') || '1', 10);
  const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);

  let filtered = audits.filter((a) => a.title.toLowerCase().includes(q.toLowerCase()));
  if (status) {
    filtered = filtered.filter((a) => a.status === status);
  }

  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const pageItems = filtered.slice(start, end);

  return NextResponse.json({ data: pageItems, total, page, pageSize });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const id = String(Date.now());
    const item: Audit = {
      id,
      title: body.title || 'Untitled audit',
      description: body.description || '',
      status: 'Open',
      auditor: body.auditor || null,
      dueDate: body.dueDate || null,
      createdAt: new Date().toISOString(),
    };
    audits.unshift(item);
    return NextResponse.json({ data: item }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}
