'use client';

import { useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Service } from '@/data/servicesData';

interface ServiceModalProps {
  service: Service | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function ServiceModal({ service, isOpen, onClose }: ServiceModalProps) {
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

  if (!isOpen || !service) return null;

  return (
    <div 
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fadeIn" />
      
      {/* Modal */}
      <div 
        className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto overflow-x-hidden glass-panel rounded-[24px] border border-white/20 animate-slideUp"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative p-8 pb-4">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl" />
          
          <div className="flex items-start justify-between relative z-10">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/10 flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-2xl">
                  {service.icon}
                </span>
              </div>
              <div>
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Professional Service
                </span>
                <h3 className="text-2xl font-bold text-white">{service.title}</h3>
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
        <div className="px-8 pb-4">
          <p className="text-slate-300 leading-relaxed mb-6">
            {service.fullDescription}
          </p>
          
          {/* Features */}
          <h4 className="text-sm font-mono text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">checklist</span>
            Key Features
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            {service.features.map((feature, index) => (
              <div 
                key={index}
                className="flex items-start gap-3 p-3 rounded-xl bg-white/5 border border-white/5"
              >
                <span className="material-symbols-outlined text-white text-sm mt-0.5">
                  check_circle
                </span>
                <span className="text-sm text-slate-300">{feature}</span>
              </div>
            ))}
          </div>

          {/* Benefits */}
          <h4 className="text-sm font-mono text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">trending_up</span>
            Benefits
          </h4>
          <div className="space-y-3">
            {service.benefits.map((benefit, index) => (
              <div 
                key={index}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5"
              >
                <span className="material-symbols-outlined text-white text-sm">
                  star
                </span>
                <span className="text-sm text-slate-300">{benefit}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-8 pt-4 border-t border-white/5">
          <Link
            href={service.ctaUrl}
            className="w-full flex items-center justify-center gap-2 py-4 px-6 rounded-xl bg-white hover:bg-gray-100 text-black font-bold transition-all transform hover:-translate-y-0.5"
          >
            <span>{service.ctaText}</span>
            <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
