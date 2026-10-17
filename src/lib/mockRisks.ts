export interface Risk {
  id: string;
  title: string;
  description?: string;
  level: 'Low' | 'Medium' | 'High' | 'Critical';
  owner?: string | null;
  status: 'Open' | 'In Progress' | 'Closed' | 'Mitigated';
  createdAt: string;
  updatedAt?: string | null;
}

export const risks: Risk[] = [
  {
    id: 'r1',
    title: 'Unpatched server vulnerability',
    description: 'Production server missing critical security patches.',
    level: 'High',
    owner: 'Jane Doe',
    status: 'Open',
    createdAt: new Date('2026-06-01').toISOString(),
    updatedAt: null,
  },
  {
    id: 'r2',
    title: 'Weak password policy',
    description: 'Current policy allows passwords under 8 characters.',
    level: 'Medium',
    owner: 'John Smith',
    status: 'In Progress',
    createdAt: new Date('2026-06-05').toISOString(),
    updatedAt: null,
  },
  {
    id: 'r3',
    title: 'Third-party vendor data access',
    description: 'Vendor has broader data access than required.',
    level: 'Critical',
    owner: null,
    status: 'Open',
    createdAt: new Date('2026-06-10').toISOString(),
    updatedAt: null,
  },
];