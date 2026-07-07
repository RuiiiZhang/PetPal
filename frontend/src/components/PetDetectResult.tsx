'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';

interface PetDetectResultProps {
  breed: string | null;
}

export default function PetDetectResult({ breed }: PetDetectResultProps) {
  const { t } = useI18n();

  if (!breed) return null;

  return (
    <div className="flex items-center gap-4 p-4 rounded-xl bg-panel-lighter border border-border-subtle animate-fade-in">
      {/* Icon */}
      <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-accent">
          <path d="M12 21C12 21 4 15 4 9.5C4 7 6 5 8.5 5C10 5 11.5 6 12 7C12.5 6 14 5 15.5 5C18 5 20 7 20 9.5C20 15 12 21 12 21Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="9" cy="10" r="0.5" fill="currentColor"/>
          <circle cx="15" cy="10" r="0.5" fill="currentColor"/>
        </svg>
      </div>

      {/* Info */}
      <div>
        <p className="text-text-muted text-[11px] tracking-widest uppercase mb-0.5">
          {t('upload.breedDetected')}
        </p>
        <p className="text-text-primary text-sm font-medium tracking-wide">
          {breed}
        </p>
      </div>

      {/* Check indicator */}
      <div className="ml-auto w-6 h-6 rounded-full bg-accent/15 flex items-center justify-center">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#d4a574" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>
    </div>
  );
}
