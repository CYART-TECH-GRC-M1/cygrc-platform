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

// Import the same in-memory array via module cache by referencing parent module
// eslint-disable-next-line @typescript-eslint/no-var-requires
const auditsModule = require('../route');
let audits: Audit[] = auditsModule && auditsModule.__esModule ? auditsModule.default ?? auditsModule.audits ?? [] : [];

export async function GET(req: Request, context: { params: Promise<{ id: string }> }) {
  const params = await context.params;
  const id = params.id;
  const found = audits.find((a) => a.id === id);
  if (!found) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json({ data: found });
}

export async function PUT(req: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const params = await context.params;
    const id = params.id;
    const body = await req.json();
    const idx = audits.findIndex((a) => a.id === id);
    if (idx === -1) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    audits[idx] = { ...audits[idx], ...body };
    return NextResponse.json({ data: audits[idx] });
  } catch (err) {
    return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });
  }
}
