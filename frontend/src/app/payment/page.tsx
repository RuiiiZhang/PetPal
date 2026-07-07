'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { createPayment } from '@/lib/api';
import OrderSummary from '@/components/OrderSummary';
import PaymentButton from '@/components/PaymentButton';

export default function PaymentPage() {
  const { t } = useI18n();
  const router = useRouter();
  const {
    orderId, setCurrentStep, setPaymentUrl, setPaymentStatus, addToast,
  } = useStore();

  const [payingMethod, setPayingMethod] = useState<'wechat' | 'alipay' | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    setCurrentStep(5);
  }, [setCurrentStep]);

  useEffect(() => {
    if (!orderId) {
      router.push('/upload');
    }
  }, [orderId, router]);

  const handlePayment = async (method: 'wechat' | 'alipay') => {
    if (!orderId) return;

    setPayingMethod(method);
    setIsProcessing(true);

    try {
      const result = await createPayment(orderId);
      setPaymentUrl(result.payment_url);
      setPaymentStatus('pending');

      // In production, redirect to payment gateway or open QR code
      // For now, simulate a successful payment after redirect
      if (result.payment_url) {
        window.open(result.payment_url, '_blank');
      }

      // Simulate payment success (replace with webhook/polling in production)
      setTimeout(() => {
        setPaymentStatus('paid');
        addToast({ type: 'success', message: t('toast.paymentSuccess') });
        setCurrentStep(6);
        router.push('/download');
      }, 2000);
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.error');
      addToast({ type: 'error', message });
    } finally {
      setIsProcessing(false);
      setPayingMethod(null);
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-start justify-center px-6 py-12">
      <div className="w-full max-w-lg animate-fade-in-up">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-3">
            {t('payment.title')}
          </h1>
          <p className="text-text-secondary text-sm tracking-wider">
            {t('payment.subtitle')}
          </p>
        </div>

        {/* Order Summary */}
        <div className="mb-8">
          <OrderSummary />
        </div>

        {/* Payment Methods */}
        <div className="space-y-4">
          <p className="text-text-muted text-xs tracking-[0.2em] uppercase text-center mb-6">
            {t('common.language') === 'Language' ? 'Select Payment Method' : '选择支付方式'}
          </p>

          <PaymentButton
            method="wechat"
            onClick={() => handlePayment('wechat')}
            isLoading={isProcessing && payingMethod === 'wechat'}
          />

          <PaymentButton
            method="alipay"
            onClick={() => handlePayment('alipay')}
            isLoading={isProcessing && payingMethod === 'alipay'}
          />
        </div>

        {/* Security note */}
        <div className="mt-8 text-center">
          <p className="text-text-muted/50 text-[11px] tracking-wider">
            🔒 {t('common.language') === 'Language' ? 'Secure payment encrypted end-to-end' : '支付信息全程加密'}
          </p>
        </div>
      </div>
    </div>
  );
}
