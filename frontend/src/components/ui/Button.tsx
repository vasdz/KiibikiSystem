import React from 'react';
import { twMerge } from 'tailwind-merge';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'ghost';
  isLoading?: boolean;
}

export const Button = ({ className, variant = 'primary', isLoading, children, ...props }: ButtonProps) => {
  const baseStyles = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2";

  const variants = {
    primary: "bg-emerald-500 text-slate-950 hover:bg-emerald-500/90 shadow-[0_0_15px_rgba(16,185,129,0.5)] font-bold",
    outline: "border border-slate-700 bg-transparent hover:bg-slate-800 text-slate-100",
    ghost: "hover:bg-slate-800 text-slate-300 hover:text-white"
  };

  return (
    <button
      className={twMerge(baseStyles, variants[variant], className)}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-slate-900 border-t-transparent" />
      ) : null}
      {children}
    </button>
  );
};
