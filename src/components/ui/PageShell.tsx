import React from "react";

export default function PageShell({
  title,
  subtitle,
  children,
  action,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <main className="flex-1 px-6 py-6 lg:px-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            {title}
          </h1>

          {subtitle && (
            <p className="mt-2 text-sm text-zinc-400">
              {subtitle}
            </p>
          )}
        </div>

        {action}
      </div>

      <div className="mt-6">
        {children}
      </div>
    </main>
  );
}