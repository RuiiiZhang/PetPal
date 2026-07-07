'use client';

import React, { useEffect } from 'react';
import { useStore } from '@/lib/store';

export default function ToastContainer() {
  const { toasts, removeToast } = useStore();

  useEffect(() => {
    toasts.forEach((toast) => {
      const timer = setTimeout(() => {
        removeToast(toast.id);
      }, 4000);
      return () => clearTimeout(timer);
    });
  }, [toasts, removeToast]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[200] flex flex-col gap-3">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`
            flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-elegant backdrop-blur-xl
            border min-w-[280px] max-w-[400px]
            animate-[toast-in_0.4s_cubic-bezier(0.16,1,0.3,1)_forwards]
            ${toast.type === 'success'
              ? 'bg-[#161616]/90 border-accent/20 text-text-primary'
              : toast.type === 'error'
                ? 'bg-[#161616]/90 border-red-500/20 text-text-primary'
                : 'bg-[#161616]/90 border-border-medium text-text-primary'
            }
          `}
        >
          {/* Icon */}
          <div className={`
            w-5 h-5 rounded-full flex items-center justify-center shrink-0
            ${toast.type === 'success' ? 'text-accent' : toast.type === 'error' ? 'text-red-400' : 'text-text-muted'}
          `}>
            {toast.type === 'success' && (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            )}
            {toast.type === 'error' && (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            )}
            {toast.type === 'info' && (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
            )}
          </div>

          {/* Message */}
          <p className="text-sm tracking-wide flex-1">{toast.message}</p>

          {/* Close */}
          <button
            onClick={() => removeToast(toast.id)}
            className="text-text-muted hover:text-text-secondary transition-colors shrink-0"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
