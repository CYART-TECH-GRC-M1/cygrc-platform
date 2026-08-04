export interface Evidence {
  id: string;
  title: string;
  description?: string;
  fileUrl?: string;
  fileName?: string;
  linkedControlId?: string | null;
  status: 'Pending' | 'Approved' | 'Rejected';
  uploadedBy?: string | null;
  createdAt: string;
  updatedAt?: string | null;
}

export const evidences: Evidence[] = [
  {
    id: 'e1',
    title: 'Access Control Audit Log',
    description: 'System-generated log showing access control enforcement.',
    fileUrl: '',
    fileName: 'access-audit-log.pdf',
    linkedControlId: 'c1',
    status: 'Approved',
    uploadedBy: 'Jane Doe',
    createdAt: new Date('2026-06-02').toISOString(),
    updatedAt: null,
  },
  {
    id: 'e2',
    title: 'Encryption Configuration Screenshot',
    description: 'Screenshot showing encryption settings enabled.',
    fileUrl: '',
    fileName: 'encryption-config.png',
    linkedControlId: 'c2',
    status: 'Pending',
    uploadedBy: 'John Smith',
    createdAt: new Date('2026-06-06').toISOString(),
    updatedAt: null,
  },
];