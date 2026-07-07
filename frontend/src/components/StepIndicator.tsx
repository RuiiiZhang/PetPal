'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';

const STEPS = [
  { key: 'upload', labelKey: 'step.upload' },
  { key: 'style', labelKey: 'step.style' },
  { key: 'preview', labelKey: 'step.preview' },
  { key: 'animation', labelKey: 'step.animation' },
  { key: 'payment', labelKey: 'step.payment' },
  { key: 'download', labelKey: 'step.download' },
];

export default function StepIndicator() {
  const { t } = useI18n();
  const currentStep = useStore((s) => s.currentStep);

  return (
    <div className="flex items-center gap-1">
      {STEPS.map((step, index) => {
        const stepNum = index + 1;
        const isActive = stepNum === currentStep;
        const isCompleted = stepNum < currentStep;

        return (
          <React.Fragment key={step.key}>
            {/* Step dot */}
            <div className="flex items-center gap-2">
              <div
                className={`
                  relative flex items-center justify-center w-7 h-7 rounded-full transition-all duration-700 ease-elegant
                  ${isActive
                    ? 'bg-accent text-text-inverse shadow-glow'
                    : isCompleted
                      ? 'bg-accent/20 text-accent'
                      : 'bg-panel-lighter text-text-muted'
                  }
                `}
              >
                {isCompleted ? (
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <span className="text-[10px] font-medium tracking-wide">{stepNum}</span>
                )}
                {isActive && (
                  <span className="absolute inset-0 rounded-full bg-accent/30 animate-gentle-pulse" />
                )}
              </div>
              <span
                className={`
                  hidden lg:block text-xs tracking-wide transition-all duration-500
                  ${isActive ? 'text-text-primary' : isCompleted ? 'text-text-secondary' : 'text-text-muted'}
                `}
              >
                {t(step.labelKey)}
              </span>
            </div>

            {/* Connector line */}
            {index < STEPS.length - 1 && (
              <div className="w-6 lg:w-10 h-px mx-1 relative overflow-hidden">
                <div className="absolute inset-0 bg-border-subtle" />
                <div
                  className={`
                    absolute inset-y-0 left-0 transition-all duration-700 ease-elegant
                    ${isCompleted ? 'w-full bg-accent/50' : 'w-0 bg-accent/50'}
                  `}
                />
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
