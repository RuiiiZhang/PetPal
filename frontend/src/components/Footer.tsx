'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';

export default function Footer() {
  const { t } = useI18n();

  return (
    <footer className="border-t border-border-subtle mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Left: Brand */}
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded bg-accent/10 flex items-center justify-center">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" className="text-accent">
                <path d="M12 21C12 21 4 15 4 9.5C4 7 6 5 8.5 5C10 5 11.5 6 12 7C12.5 6 14 5 15.5 5C18 5 20 7 20 9.5C20 15 12 21 12 21Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="text-xs text-text-muted tracking-wider">
              {t('footer.copyright')}
            </span>
          </div>

          {/* Right: Links */}
          <div className="flex items-center gap-6">
            <a href="#" className="text-xs text-text-muted hover:text-text-secondary transition-colors duration-300 tracking-wide">
              {t('footer.privacy')}
            </a>
            <a href="#" className="text-xs text-text-muted hover:text-text-secondary transition-colors duration-300 tracking-wide">
              {t('footer.terms')}
            </a>
            <a href="#" className="text-xs text-text-muted hover:text-text-secondary transition-colors duration-300 tracking-wide">
              {t('footer.contact')}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
