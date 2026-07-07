'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';

interface PaymentButtonProps {
  method: 'wechat' | 'alipay';
  onClick: () => void;
  isLoading?: boolean;
}

export default function PaymentButton({ method, onClick, isLoading = false }: PaymentButtonProps) {
  const { t } = useI18n();
  const isWechat = method === 'wechat';

  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`
        w-full flex items-center justify-center gap-3 py-4 rounded-xl text-sm font-medium tracking-wide
        transition-all duration-500 ease-elegant
        hover:scale-[1.01] active:scale-[0.99]
        disabled:opacity-60 disabled:cursor-not-allowed
        ${isWechat
          ? 'bg-[#07C160] text-white hover:bg-[#06ae56] shadow-lg shadow-[#07C160]/20'
          : 'bg-[#1677FF] text-white hover:bg-[#0e6fe6] shadow-lg shadow-[#1677FF]/20'
        }
      `}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          {t('payment.processing')}
        </span>
      ) : (
        <>
          {/* Payment icon */}
          <div className="w-6 h-6 flex items-center justify-center">
            {isWechat ? (
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.825 4.58c-3.794 0-7.075 2.457-7.075 5.742 0 3.285 3.281 5.742 7.075 5.742.833 0 1.64-.126 2.396-.352a.726.726 0 0 1 .6.082l1.588.93a.273.273 0 0 0 .14.045c.133 0 .243-.11.243-.245 0-.06-.024-.119-.04-.177l-.326-1.233a.495.495 0 0 1 .178-.555C21.855 19.508 22.86 17.828 22.86 16.313c0-3.285-2.64-5.742-6.437-5.742zm-2.344 3.167c.536 0 .97.44.97.983a.976.976 0 0 1-.97.983.976.976 0 0 1-.97-.983c0-.542.434-.983.97-.983zm4.688 0c.536 0 .97.44.97.983a.976.976 0 0 1-.97.983.976.976 0 0 1-.97-.983c0-.542.434-.983.97-.983z"/>
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M11.984 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.016 0zm5.568 8.16c-.168 1.684-.864 3.696-1.92 5.544-.756 1.32-1.596 2.436-2.52 3.264-.54.48-.924.756-1.152.876-.276.132-.54.084-.756-.12-.216-.204-.168-.48.084-.876.12-.192.348-.48.672-.864.324-.384.756-.876 1.296-1.476-.54-.036-1.2-.216-1.98-.54-.78-.324-1.476-.756-2.088-1.296-.612-.54-1.044-1.116-1.296-1.728-.252-.612-.288-1.224-.108-1.836.18-.612.516-1.128 1.008-1.548.492-.42 1.056-.708 1.692-.864.636-.156 1.26-.168 1.872-.036.612.132 1.116.396 1.512.792.396.396.648.876.756 1.44.108.564.072 1.152-.108 1.764-.18.612-.468 1.224-.864 1.836.66.228 1.224.516 1.692.864.468.348.84.744 1.116 1.188.276.444.42.9.432 1.368.012.468-.108.924-.36 1.368z"/>
              </svg>
            )}
          </div>
          <span>{isWechat ? t('payment.wechat') : t('payment.alipay')}</span>
        </>
      )}
    </button>
  );
}
