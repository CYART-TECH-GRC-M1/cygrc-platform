"use client";
import React from "react";

type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string | null;
};

const Input = React.forwardRef<HTMLInputElement, InputProps>((props, ref) => {
  const { label, error, className = "", ...rest } = props;
  return (
    <div>
      {label && <label className="mb-2 block text-sm font-medium text-slate-300">{label}</label>}
      <input
        ref={ref}
        {...rest}
        className={
          "mt-1 w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-600/50 " +
          className
        }
      />
      {error && <p className="mt-2 text-sm text-rose-400">{error}</p>}
    </div>
  );
});

Input.displayName = "Input";
export default Input;
