import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-pulse-600 hover:bg-pulse-500 text-white shadow-lg shadow-pulse-900/30 border border-pulse-500/20",
  secondary:
    "glass-inset hover:bg-slate-800/80 text-slate-100 border border-white/10",
  ghost: "bg-transparent hover:bg-white/5 text-slate-300 border border-transparent",
};

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`press-feedback rounded-lg px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
