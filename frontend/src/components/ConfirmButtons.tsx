'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';

interface ConfirmButtonsProps {
  onConfirm: () => void;
  onRedo: () => void;
  onAdjust?: () => void;
  confirmLabel?: string;
  redoLabel?: string;
  adjustLabel?: string;
  isConfirming?: boolean;
}

export default function ConfirmButtons({
  onConfirm,
  onRedo,
  onAdjust,
  confirmLabel,
  redoLabel,
  adjustLabel,
  isConfirming = false,
}: ConfirmButtonsProps) {
  const { t } = useI18n();

  return (
    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10">
      {/* Primary: Confirm */}
      <button
        onClick={onConfirm}
        disabled={isConfirming}
        className="
          relative px-10 py-3.5 rounded-xl bg-accent text-text-inverse text-sm font-medium tracking-wide
          transition-all duration-500 ease-elegant
          hover:shadow-glow hover:scale-[1.02]
          active:scale-[0.98]
          disabled:opacity-60 disabled:cursor-not-allowed
          min-w-[180px]
        "
      >
        {isConfirming ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-4 h-4 border-2 border-text-inverse/30 border-t-text-inverse rounded-full animate-spin" />
            {t('preview.confirming')}
          </span>
        ) : (
          confirmLabel || t('preview.satisfied')
        )}
      </button>

      {/* Secondary: Redo */}
      <button
        onClick={onRedo}
        disabled={isConfirming}
        className="
          px-8 py-3.5 rounded-xl border border-border-medium text-text-secondary text-sm tracking-wide
          transition-all duration-500 ease-elegant
          hover:border-accent/30 hover:text-text-primary hover:bg-panel-light
          active:scale-[0.98]
          disabled:opacity-40 disabled:cursor-not-allowed
          min-w-[140px]
        "
      >
        {redoLabel || t('preview.redo')}
      </button>

      {/* Tertiary: Adjust */}
      {onAdjust && (
        <button
          onClick={onAdjust}
          disabled={isConfirming}
          className="
            px-6 py-3.5 rounded-xl text-text-muted text-sm tracking-wide
            transition-all duration-500 ease-elegant
            hover:text-text-secondary
            disabled:opacity-40 disabled:cursor-not-allowed
          "
        >
          {adjustLabel || t('preview.adjust')}
        </button>
      )}
    </div>
  );
}
