import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function Input({ label, id, className = "", ...props }: InputProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
  return (
    <label className="flex flex-col gap-1 text-sm text-slate-300" htmlFor={inputId}>
      <span>{label}</span>
      <input
        id={inputId}
        className={`rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-pulse-500 focus:ring-2 ${className}`}
        {...props}
      />
    </label>
  );
}
