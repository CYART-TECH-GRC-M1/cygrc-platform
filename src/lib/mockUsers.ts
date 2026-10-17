export interface UserRecord {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'auditor' | 'analyst' | 'viewer';
}

export const users: UserRecord[] = [
  {
    id: 'u1',
    name: 'Alex Morgan',
    email: 'alex@cygrc.io',
    role: 'admin',
  },
  {
    id: 'u2',
    name: 'Mina Patel',
    email: 'mina@cygrc.io',
    role: 'auditor',
  },
  {
    id: 'u3',
    name: 'Noah Kim',
    email: 'noah@cygrc.io',
    role: 'analyst',
  },
  {
    id: 'u4',
    name: 'Sage Chen',
    email: 'sage@cygrc.io',
    role: 'viewer',
  },
];
