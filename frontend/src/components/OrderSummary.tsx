'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { STYLES } from './StyleCard';

export default function OrderSummary() {
  const { t } = useI18n();
  const { orderId, petName, style } = useStore();

  const selectedStyle = STYLES.find((s) => s.id === style);
  const price = selectedStyle?.price || 0;

  return (
    <div className="rounded-2xl bg-panel border border-border-subtle p-8 shadow-card">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 pb-6 border-b border-border-subtle">
        <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-accent">
            <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <rect x="9" y="3" width="6" height="4" rx="1" stroke="currentColor" strokeWidth="1.5"/>
          </svg>
        </div>
        <h3 className="font-serif text-lg text-text-primary tracking-wide">
          {t('payment.title')}
        </h3>
      </div>

      {/* Order details */}
      <div className="space-y-4">
        {orderId && (
          <div className="flex justify-between items-center">
            <span className="text-text-muted text-sm tracking-wide">{t('payment.orderNo')}</span>
            <span className="text-text-secondary text-sm font-mono">{orderId.slice(0, 12)}...</span>
          </div>
        )}

        <div className="flex justify-between items-center">
          <span className="text-text-muted text-sm tracking-wide">{t('payment.petName')}</span>
          <span className="text-text-primary text-sm">{petName || '—'}</span>
        </div>

        {selectedStyle && (
          <div className="flex justify-between items-center">
            <span className="text-text-muted text-sm tracking-wide">{t('payment.selectedStyle')}</span>
            <span className="text-text-primary text-sm">{t(selectedStyle.nameKey)}</span>
          </div>
        )}

        {/* Divider */}
        <div className="pt-4 mt-4 border-t border-border-subtle">
          <div className="flex justify-between items-baseline">
            <span className="text-text-muted text-sm tracking-wide">{t('payment.amount')}</span>
            <div className="flex items-baseline gap-1">
              <span className="text-accent/60 text-sm">{t('style.price')}</span>
              <span className="font-serif text-3xl text-accent">{price}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
