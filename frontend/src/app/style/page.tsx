'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { uploadPhotos } from '@/lib/api';
import StyleCard, { STYLES } from '@/components/StyleCard';
import PetDetectResult from '@/components/PetDetectResult';
import type { PetStyle } from '@/lib/types';

export default function StylePage() {
  const { t } = useI18n();
  const router = useRouter();
  const {
    photos, petName, style, setStyle, orderId, petBreed,
    setOrderId, setPetBreed, setCurrentStep, addToast,
  } = useStore();

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setCurrentStep(2);
  }, [setCurrentStep]);

  // Guard: no photos, go back
  useEffect(() => {
    if (photos.length === 0) {
      router.push('/upload');
    }
  }, [photos.length, router]);

  const handleNext = async () => {
    if (!style) {
      addToast({ type: 'info', message: 'Please select a style' });
      return;
    }

    setIsSubmitting(true);

    try {
      if (!orderId) {
        // Upload photos with selected style
        const files = photos.map((p) => p.file);
        const result = await uploadPhotos(files, petName, style);
        setOrderId(result.order_id);
        setPetBreed(result.pet_breed);
      } else {
        // Re-upload with updated style if needed
        const files = photos.map((p) => p.file);
        const result = await uploadPhotos(files, petName, style);
        setOrderId(result.order_id);
      }

      setCurrentStep(3);
      router.push('/preview');
    } catch (err) {
      const message = err instanceof Error ? err.message : t('toast.networkError');
      addToast({ type: 'error', message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-start justify-center px-6 py-12">
      <div className="w-full max-w-4xl animate-fade-in-up">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-3">
            {t('style.title')}
          </h1>
          <p className="text-text-secondary text-sm tracking-wider">
            {t('style.subtitle')}
          </p>
        </div>

        {/* Breed detection result */}
        {petBreed && (
          <div className="max-w-md mx-auto mb-10">
            <PetDetectResult breed={petBreed} />
          </div>
        )}

        {/* Style cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {STYLES.map((styleOption, index) => (
            <div
              key={styleOption.id}
              className="animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <StyleCard
                styleOption={styleOption}
                isSelected={style === styleOption.id}
                onSelect={setStyle}
              />
            </div>
          ))}
        </div>

        {/* Next button */}
        <div className="flex justify-center">
          <button
            onClick={handleNext}
            disabled={!style || isSubmitting}
            className="
              px-12 py-4 rounded-xl bg-accent text-text-inverse text-sm font-medium tracking-wide
              transition-all duration-500 ease-elegant
              hover:shadow-glow hover:scale-[1.02]
              active:scale-[0.98]
              disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none
            "
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-text-inverse/30 border-t-text-inverse rounded-full animate-spin" />
                {t('common.loading')}
              </span>
            ) : (
              t('style.nextBtn')
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
