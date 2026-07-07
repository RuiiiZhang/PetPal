'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { generateCharacter, confirmCharacter } from '@/lib/api';
import PreviewGallery from '@/components/PreviewGallery';
import ConfirmButtons from '@/components/ConfirmButtons';
import LoadingOverlay from '@/components/LoadingOverlay';

export default function PreviewPage() {
  const { t } = useI18n();
  const router = useRouter();
  const {
    orderId, characterImageUrl, setCharacterImageUrl,
    setCurrentStep, isGenerating, setIsGenerating, addToast,
  } = useStore();

  const [isConfirming, setIsConfirming] = useState(false);

  useEffect(() => {
    setCurrentStep(3);
  }, [setCurrentStep]);

  // Guard: no order, go back
  useEffect(() => {
    if (!orderId) {
      router.push('/upload');
    }
  }, [orderId, router]);

  // Generate character on mount
  const doGenerate = useCallback(async () => {
    if (!orderId || characterImageUrl) return;

    setIsGenerating(true);
    try {
      const result = await generateCharacter(orderId);
      setCharacterImageUrl(result.image_url);
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.error');
      addToast({ type: 'error', message });
    } finally {
      setIsGenerating(false);
    }
  }, [orderId, characterImageUrl, setCharacterImageUrl, setIsGenerating, addToast, t]);

  useEffect(() => {
    doGenerate();
  }, [doGenerate]);

  const handleConfirm = async () => {
    if (!orderId) return;
    setIsConfirming(true);

    try {
      await confirmCharacter(orderId, true);
      setCurrentStep(4);
      router.push('/animation');
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.error');
      addToast({ type: 'error', message });
    } finally {
      setIsConfirming(false);
    }
  };

  const handleRedo = async () => {
    setCharacterImageUrl(null as unknown as string);
    // Clear and regenerate
    useStore.getState().setCharacterImageUrl('');
    try {
      setIsGenerating(true);
      const result = await generateCharacter(orderId!);
      setCharacterImageUrl(result.image_url);
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
          message={t('preview.generating')}
          subMessage={t('preview.processing')}
        />
      )}

      <div className="min-h-[calc(100vh-5rem)] flex items-start justify-center px-6 py-12">
        <div className="w-full max-w-3xl animate-fade-in-up">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-3">
              {t('preview.title')}
            </h1>
            <p className="text-text-secondary text-sm tracking-wider">
              {t('preview.subtitle')}
            </p>
          </div>

          {/* Preview gallery - large and centered */}
          <div className="mb-8">
            <PreviewGallery
              imageUrl={characterImageUrl}
              type="image"
            />
          </div>

          {/* Action buttons */}
          {characterImageUrl && (
            <ConfirmButtons
              onConfirm={handleConfirm}
              onRedo={handleRedo}
              onAdjust={() => {}}
              isConfirming={isConfirming}
            />
          )}
        </div>
      </div>
    </>
  );
}
