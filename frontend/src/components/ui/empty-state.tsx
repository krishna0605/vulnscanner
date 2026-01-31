import React from 'react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: string;
  title?: string;
  message?: string;
  className?: string;
}

export function EmptyState({
  icon = 'info',
  title = 'No Data',
  message = 'No data available yet.',
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center h-full min-h-[200px] bg-white/[0.02] rounded-xl border border-dashed border-white/10',
        className
      )}
    >
      <span className="material-symbols-outlined text-4xl text-slate-600 mb-4">{icon}</span>
      <h3 className="text-lg font-medium text-slate-400">{title}</h3>
      <p className="text-sm text-slate-500 mt-1 max-w-[250px]">{message}</p>
    </div>
  );
}
