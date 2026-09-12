
import { Providers } from "@/components/Providers";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
<<<<<<< HEAD
=======
import RequireAuth from "@/components/ui/RequireAuth";
>>>>>>> origin/Abhishek

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
<<<<<<< HEAD
      <div className="flex min-h-screen bg-slate-950 text-slate-100">
        <Sidebar />
=======
      <RequireAuth>
        <div className="flex min-h-screen bg-slate-950 text-slate-100">
          <Sidebar />
>>>>>>> origin/Abhishek

        <div className="flex min-w-0 flex-1 flex-col bg-slate-950">
          <TopNav />

          <main className="mx-auto flex-1 w-full max-w-[1600px] bg-slate-950 p-6 animate-fade-in md:p-8">
            {children}
          </main>

          <footer className="flex h-12 items-center justify-center border-t border-slate-800 bg-slate-950 text-xs text-slate-500">
            © {new Date().getFullYear()} CyGRC Platform. All rights reserved. v1.0.0
          </footer>
        </div>
<<<<<<< HEAD
      </div>
=======
        </div>
      </RequireAuth>
>>>>>>> origin/Abhishek
    </Providers>
  );
}

