'use client';

import { useEffect, useCallback } from 'react';
import { Resource } from '@/data/securityConcepts';

interface ResourcesModalProps {
  resources: Resource[];
  isOpen: boolean;
  onClose: () => void;
}

export default function ResourcesModal({ resources, isOpen, onClose }: ResourcesModalProps) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fadeIn" />
      
      {/* Modal */}
      <div 
        className="relative w-full max-w-lg glass-panel rounded-[24px] border border-white/20 overflow-hidden animate-slideUp"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative p-8 pb-4">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl" />
          
          <div className="flex items-start justify-between relative z-10">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/10 flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-2xl">
                  library_books
                </span>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Security Resources</h3>
                <p className="text-sm text-slate-400 font-mono">Trusted industry sources</p>
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors"
            >
              <span className="material-symbols-outlined text-slate-400 hover:text-white">
                close
              </span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="px-8 pb-8 space-y-4">
          {resources.map((resource) => (
            <a
              key={resource.id}
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-interactive-dark flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-white">
                    {resource.icon}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-white">{resource.name}</h4>
                    <span className="material-symbols-outlined text-slate-500 text-sm group-hover:translate-x-1 transition-transform">
                      open_in_new
                    </span>
                  </div>
                  <p className="text-sm text-slate-400">{resource.description}</p>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
