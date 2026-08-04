export interface Control {
  id: string;
  title: string;
  description?: string;
  framework?: string;
  status: 'Implemented' | 'In Progress' | 'Not Implemented' | 'Not Applicable';
  owner?: string | null;
  createdAt: string;
  updatedAt?: string | null;
}

export const controls: Control[] = [
  {
    id: 'c1',
    title: 'Access Control Policy',
    description: 'Enforce role-based access control across all systems.',
    framework: 'ISO 27001',
    status: 'Implemented',
    owner: 'Jane Doe',
    createdAt: new Date('2026-06-01').toISOString(),
    updatedAt: null,
  },
  {
    id: 'c2',
    title: 'Data Encryption Standard',
    description: 'Ensure data at rest and in transit is encrypted.',
    framework: 'SOC 2',
    status: 'In Progress',
    owner: 'John Smith',
    createdAt: new Date('2026-06-05').toISOString(),
    updatedAt: null,
  },
  {
    id: 'c3',
    title: 'Vendor Risk Assessment',
    description: 'Periodic assessment of third-party vendor security posture.',
    framework: 'NIST',
    status: 'Not Implemented',
    owner: null,
    createdAt: new Date('2026-06-10').toISOString(),
    updatedAt: null,
  },
];