'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';
import { resolveImageUrl } from '@/lib/api';
import type { DownloadFile } from '@/lib/types';

interface DownloadCardProps {
  file: DownloadFile;
}

export default function DownloadCard({ file }: DownloadCardProps) {
  const { t } = useI18n();

  const typeLabels: Record<string, string> = {
    desktop_pet: t('download.desktopPet'),
    sticker_pack: t('download.stickerPack'),
    guide: t('download.userGuide'),
  };

  const typeIcons: Record<string, React.ReactNode> = {
    desktop_pet: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <line x1="8" y1="21" x2="16" y2="21" />
        <line x1="12" y1="17" x2="12" y2="21" />
      </svg>
    ),
    sticker_pack: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        <path d="M12 7v5l3 3" />
      </svg>
    ),
    guide: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
  };

  const handleDownload = () => {
    const url = resolveImageUrl(file.url);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    link.click();
  };

  return (
    <div className="group flex items-center gap-5 p-5 rounded-xl bg-panel border border-border-subtle hover:border-border-medium hover:bg-panel-light transition-all duration-500">
      {/* Icon */}
      <div className="w-12 h-12 rounded-xl bg-accent/8 flex items-center justify-center text-accent shrink-0 transition-colors duration-500 group-hover:bg-accent/15">
        {typeIcons[file.type] || typeIcons.guide}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h4 className="text-text-primary text-sm font-medium tracking-wide mb-1">
          {typeLabels[file.type] || file.name}
        </h4>
        <p className="text-text-muted text-xs tracking-wider">
          {file.name} · {file.size}
        </p>
      </div>

      {/* Download button */}
      <button
        onClick={handleDownload}
        className="
          shrink-0 px-5 py-2.5 rounded-lg text-xs font-medium tracking-wider
          bg-accent/10 text-accent border border-accent/20
          hover:bg-accent hover:text-text-inverse hover:border-accent
          transition-all duration-500 ease-elegant
          active:scale-[0.97]
        "
      >
        <span className="flex items-center gap-2">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Download
        </span>
      </button>
    </div>
  );
}
