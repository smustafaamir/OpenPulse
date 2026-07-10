import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Card({ title, action, children, className = "" }: CardProps) {
  return (
    <section
      className={`rounded-xl border border-slate-800 bg-slate-900/70 p-4 shadow-xl shadow-black/20 ${className}`}
    >
      {(title || action) && (
        <header className="mb-4 flex items-center justify-between gap-3">
          {title ? <h2 className="text-lg font-semibold text-slate-100">{title}</h2> : <span />}
          {action}
        </header>
      )}
      {children}
    </section>
  );
}
