'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';

interface LoadingOverlayProps {
  message?: string;
  subMessage?: string;
}

export default function LoadingOverlay({ message, subMessage }: LoadingOverlayProps) {
  const { t } = useI18n();

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-surface/90 backdrop-blur-xl">
      <div className="flex flex-col items-center gap-8 max-w-sm mx-auto px-6">
        {/* Elegant loading animation - orbiting dots */}
        <div className="relative w-24 h-24">
          {/* Outer ring */}
          <div className="absolute inset-0 rounded-full border border-accent/10" />
          
          {/* Orbiting dot 1 */}
          <div className="absolute inset-0 animate-[spin_3s_linear_infinite]">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full bg-accent shadow-[0_0_12px_rgba(212,165,116,0.6)]" />
          </div>
          
          {/* Orbiting dot 2 */}
          <div className="absolute inset-0 animate-[spin_3s_linear_infinite_reverse]">
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-accent/60 shadow-[0_0_8px_rgba(212,165,116,0.4)]" />
          </div>
          
          {/* Orbiting dot 3 */}
          <div className="absolute inset-2 animate-[spin_2s_linear_infinite]">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-accent/40" />
          </div>

          {/* Center icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center animate-gentle-pulse">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-accent">
                <path d="M12 21C12 21 4 15 4 9.5C4 7 6 5 8.5 5C10 5 11.5 6 12 7C12.5 6 14 5 15.5 5C18 5 20 7 20 9.5C20 15 12 21 12 21Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Text */}
        <div className="text-center space-y-2">
          <p className="font-serif text-lg text-text-primary tracking-wide animate-shimmer">
            {message || t('preview.generating')}
          </p>
          {subMessage && (
            <p className="text-text-muted text-sm tracking-wider">
              {subMessage}
            </p>
          )}
        </div>

        {/* Progress bar */}
        <div className="w-48 h-0.5 rounded-full bg-border-subtle overflow-hidden">
          <div className="h-full w-1/3 bg-accent/60 rounded-full animate-progress" />
        </div>
      </div>
    </div>
  );
}
