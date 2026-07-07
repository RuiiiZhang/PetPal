'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { uploadPhotos } from '@/lib/api';
import PhotoUploader from '@/components/PhotoUploader';
import PetDetectResult from '@/components/PetDetectResult';

export default function UploadPage() {
  const { t } = useI18n();
  const router = useRouter();
  const {
    photos, petName, setPetName, setOrderId, setPetBreed, setCurrentStep,
    addToast,
  } = useStore();

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentStep(1);
  }, [setCurrentStep]);

  const handleNext = async () => {
    // Validation
    if (photos.length === 0) {
      setError(t('upload.atLeastOne'));
      addToast({ type: 'error', message: t('upload.atLeastOne') });
      return;
    }
    if (!petName.trim()) {
      setError(t('upload.enterName'));
      addToast({ type: 'error', message: t('upload.enterName') });
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      const files = photos.map((p) => p.file);
      const result = await uploadPhotos(files, petName.trim(), 'cute'); // style will be set on next page
      setOrderId(result.order_id);
      setPetBreed(result.pet_breed);
      setCurrentStep(2);
      router.push('/style');
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.networkError');
      addToast({ type: 'error', message });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-start justify-center px-6 py-12">
      <div className="w-full max-w-2xl animate-fade-in-up">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-3">
            {t('upload.title')}
          </h1>
          <p className="text-text-secondary text-sm tracking-wider">
            {t('upload.subtitle')}
          </p>
        </div>

        {/* Content */}
        <div className="space-y-8">
          {/* Photo uploader */}
          <PhotoUploader />

          {/* Pet name input */}
          <div className="space-y-3">
            <label className="block text-text-muted text-xs tracking-[0.2em] uppercase">
              {t('upload.petName')}
            </label>
            <input
              type="text"
              value={petName}
              onChange={(e) => {
                setPetName(e.target.value);
                setError(null);
              }}
              placeholder={t('upload.petNamePlaceholder')}
              className="
                w-full px-5 py-4 rounded-xl bg-panel border border-border-subtle
                text-text-primary text-sm tracking-wide placeholder:text-text-muted/50
                focus:border-accent/30 focus:bg-panel-light
                outline-none transition-all duration-500
              "
            />
          </div>

          {/* Error message */}
          {error && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/5 border border-red-500/10 animate-fade-in">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span className="text-red-400/80 text-sm">{error}</span>
            </div>
          )}

          {/* Next button */}
          <button
            onClick={handleNext}
            disabled={isUploading}
            className="
              w-full py-4 rounded-xl bg-accent text-text-inverse text-sm font-medium tracking-wide
              transition-all duration-500 ease-elegant
              hover:shadow-glow hover:scale-[1.01]
              active:scale-[0.99]
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {isUploading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-text-inverse/30 border-t-text-inverse rounded-full animate-spin" />
                {t('common.loading')}
              </span>
            ) : (
              t('upload.nextBtn')
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
