import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  className = "",
  disabled,
  ...props
}) => {
  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs font-medium rounded-md",
    md: "px-4 py-2 text-sm font-medium rounded-lg",
    lg: "px-6 py-3 text-base font-semibold rounded-lg",
  };

  const variantStyles = {
    primary: "bg-sky-600 hover:bg-sky-700 text-white shadow-sm focus:ring-2 focus:ring-sky-500 focus:ring-offset-2",
    secondary: "bg-slate-800 hover:bg-slate-900 text-white shadow-sm",
    outline: "border border-slate-300 hover:bg-slate-50 text-slate-700 bg-white shadow-xs",
    danger: "bg-rose-600 hover:bg-rose-700 text-white shadow-sm",
    ghost: "hover:bg-slate-100 text-slate-600",
  };

  return (
    <button
      className={`inline-flex items-center justify-center transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};
