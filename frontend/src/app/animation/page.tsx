'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { generateAnimation, confirmAnimation } from '@/lib/api';
import PreviewGallery from '@/components/PreviewGallery';
import ConfirmButtons from '@/components/ConfirmButtons';
import LoadingOverlay from '@/components/LoadingOverlay';

export default function AnimationPage() {
  const { t } = useI18n();
  const router = useRouter();
  const {
    orderId, animationUrl, setAnimationUrl,
    setCurrentStep, isGenerating, setIsGenerating, addToast,
  } = useStore();

  const [isConfirming, setIsConfirming] = useState(false);

  useEffect(() => {
    setCurrentStep(4);
  }, [setCurrentStep]);

  useEffect(() => {
    if (!orderId) {
      router.push('/upload');
    }
  }, [orderId, router]);

  // Generate animation on mount
  const doGenerate = useCallback(async () => {
    if (!orderId || animationUrl) return;

    setIsGenerating(true);
    try {
      const result = await generateAnimation(orderId);
      setAnimationUrl(result.image_url);
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.error');
      addToast({ type: 'error', message });
    } finally {
      setIsGenerating(false);
    }
  }, [orderId, animationUrl, setAnimationUrl, setIsGenerating, addToast, t]);

  useEffect(() => {
    doGenerate();
  }, [doGenerate]);

  const handleConfirm = async () => {
    if (!orderId) return;
    setIsConfirming(true);

    try {
      await confirmAnimation(orderId, true);
      setCurrentStep(5);
      router.push('/payment');
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.error');
      addToast({ type: 'error', message });
    } finally {
      setIsConfirming(false);
    }
  };

  const handleRedo = async () => {
    setAnimationUrl('');
    try {
      setIsGenerating(true);
      const result = await generateAnimation(orderId!);
      setAnimationUrl(result.image_url);
      addToast({ type: 'success', message: 'Regenerated' });
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.error');
      addToast({ type: 'error', message });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      {isGenerating && (
        <LoadingOverlay
          message={t('animation.generating')}
          subMessage={t('animation.processing')}
        />
      )}

      <div className="min-h-[calc(100vh-5rem)] flex items-start justify-center px-6 py-12">
        <div className="w-full max-w-3xl animate-fade-in-up">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-3">
              {t('animation.title')}
            </h1>
            <p className="text-text-secondary text-sm tracking-wider">
              {t('animation.subtitle')}
            </p>
          </div>

          {/* Animation preview - large and centered */}
          <div className="mb-8">
            <PreviewGallery
              imageUrl={animationUrl}
              type="animation"
            />
          </div>

          {/* Action buttons */}
          {animationUrl && (
            <ConfirmButtons
              onConfirm={handleConfirm}
              onRedo={handleRedo}
              onAdjust={() => {}}
              confirmLabel={t('animation.satisfied')}
              redoLabel={t('animation.redo')}
              adjustLabel={t('animation.adjust')}
              isConfirming={isConfirming}
            />
          )}
        </div>
      </div>
    </>
  );
}
