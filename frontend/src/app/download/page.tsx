'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import { getDownloadLinks, resolveImageUrl } from '@/lib/api';
import DownloadCard from '@/components/DownloadCard';
import type { DownloadFile } from '@/lib/types';

export default function DownloadPage() {
  const { t } = useI18n();
  const router = useRouter();
  const {
    orderId, downloadFiles, setDownloadFiles,
    setCurrentStep, reset, addToast,
  } = useStore();

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setCurrentStep(6);
  }, [setCurrentStep]);

  useEffect(() => {
    if (!orderId) {
      router.push('/upload');
    }
  }, [orderId, router]);

  // Fetch download links
  useEffect(() => {
    const fetchDownloads = async () => {
      if (!orderId || downloadFiles) return;

      setIsLoading(true);
      try {
        const result = await getDownloadLinks(orderId);
        setDownloadFiles(result.files);
      } catch (err) {
        // Fallback mock data for demo
        setDownloadFiles([
          {
            name: 'PetPal_Desktop_v1.0.zip',
            url: '/downloads/petpal-desktop.zip',
            size: '45.2 MB',
            type: 'desktop_pet',
          },
          {
            name: 'PetPal_Stickers_v1.0.zip',
            url: '/downloads/petpal-stickers.zip',
            size: '12.8 MB',
            type: 'sticker_pack',
          },
          {
            name: 'QuickStart_Guide.pdf',
            url: '/downloads/guide.pdf',
            size: '1.2 MB',
            type: 'guide',
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDownloads();
  }, [orderId, downloadFiles, setDownloadFiles]);

  const handleDownloadAll = () => {
    if (!downloadFiles) return;
    downloadFiles.forEach((file) => {
      const url = resolveImageUrl(file.url);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name;
      link.click();
    });
    addToast({ type: 'success', message: 'Downloads started' });
  };

  const handleRestart = () => {
    reset();
    router.push('/');
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-start justify-center px-6 py-12">
      <div className="w-full max-w-2xl animate-fade-in-up">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent/10 mb-6">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" className="text-accent">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-3">
            {t('download.title')}
          </h1>
          <p className="text-text-secondary text-sm tracking-wider">
            {t('download.subtitle')}
          </p>
        </div>

        {/* Download cards */}
        <div className="space-y-4 mb-10">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-5 p-5 rounded-xl bg-panel border border-border-subtle animate-pulse">
                  <div className="w-12 h-12 rounded-xl bg-panel-lighter" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-32 bg-panel-lighter rounded" />
                    <div className="h-3 w-48 bg-panel-lighter rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            downloadFiles?.map((file) => (
              <DownloadCard key={file.name} file={file} />
            ))
          )}
        </div>

        {/* Download all button */}
        {downloadFiles && downloadFiles.length > 0 && (
          <div className="text-center mb-12">
            <button
              onClick={handleDownloadAll}
              className="
                inline-flex items-center gap-3 px-10 py-4 rounded-xl
                bg-accent text-text-inverse text-sm font-medium tracking-wide
                transition-all duration-500 ease-elegant
                hover:shadow-glow hover:scale-[1.02]
                active:scale-[0.98]
              "
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              {t('download.downloadAll')}
            </button>
          </div>
        )}

        {/* User guide */}
        <div className="rounded-2xl bg-panel border border-border-subtle p-8 mb-12">
          <h3 className="font-serif text-lg text-text-primary tracking-wide mb-6">
            {t('download.userGuide')}
          </h3>
          <ol className="space-y-4">
            {[
              t('download.guide.step1'),
              t('download.guide.step2'),
              t('download.guide.step3'),
              t('download.guide.step4'),
              t('download.guide.step5'),
            ].map((step, i) => (
              <li key={i} className="flex items-start gap-4">
                <span className="shrink-0 w-6 h-6 rounded-full bg-accent/10 flex items-center justify-center text-accent text-xs font-medium mt-0.5">
                  {i + 1}
                </span>
                <span className="text-text-secondary text-sm leading-relaxed tracking-wide">
                  {step}
                </span>
              </li>
            ))}
          </ol>
        </div>

        {/* Thank you message */}
        <div className="text-center space-y-8">
          <p className="text-text-muted text-sm tracking-wider italic font-serif">
            {t('download.thanks')}
          </p>

          <button
            onClick={handleRestart}
            className="
              inline-flex items-center gap-2 text-text-muted hover:text-accent text-sm tracking-wide
              transition-colors duration-500
            "
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="1 4 1 10 7 10" />
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
            </svg>
            {t('download.restart')}
          </button>
        </div>
      </div>
    </div>
  );
}
