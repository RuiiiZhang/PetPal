'use client';

import React from 'react';
import Link from 'next/link';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import StepIndicator from './StepIndicator';

const STEP_ROUTES = ['/upload', '/style', '/preview', '/animation', '/payment', '/download'];

export default function Header() {
  const { t, locale, setLocale } = useI18n();
  const currentStep = useStore((s) => s.currentStep);
  const isWorkflowPage = currentStep > 0;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface/80 backdrop-blur-xl border-b border-border-subtle">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors duration-500">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-accent">
              <path d="M12 21C12 21 4 15 4 9.5C4 7 6 5 8.5 5C10 5 11.5 6 12 7C12.5 6 14 5 15.5 5C18 5 20 7 20 9.5C20 15 12 21 12 21Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="font-serif text-lg text-text-primary tracking-wide">
            {t('common.appName')}
          </span>
        </Link>

        {/* Center: Step Indicator (workflow pages only) */}
        {isWorkflowPage && (
          <div className="hidden md:block">
            <StepIndicator />
          </div>
        )}

        {/* Right: Language toggle */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setLocale(locale === 'zh' ? 'en' : 'zh')}
            className="text-xs text-text-secondary hover:text-text-primary transition-colors duration-300 tracking-widest uppercase px-3 py-1.5 rounded-full border border-border-subtle hover:border-border-medium"
          >
            {locale === 'zh' ? 'EN' : '中文'}
          </button>
        </div>
      </div>

      {/* Mobile step indicator */}
      {isWorkflowPage && (
        <div className="md:hidden px-6 pb-3">
          <StepIndicator />
        </div>
      )}
    </header>
  );
}
