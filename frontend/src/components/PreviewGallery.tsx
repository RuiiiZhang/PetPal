'use client';

import React from 'react';
import { resolveImageUrl } from '@/lib/api';

interface PreviewGalleryProps {
  imageUrl: string | null;
  type?: 'image' | 'animation';
}

export default function PreviewGallery({ imageUrl, type = 'image' }: PreviewGalleryProps) {
  if (!imageUrl) {
    return (
      <div className="w-full aspect-square max-w-2xl mx-auto rounded-2xl bg-panel-lighter border border-border-subtle flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-2xl bg-panel rounded-xl flex items-center justify-center mx-auto mb-4">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-text-muted">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.5"/>
              <circle cx="8.5" cy="8.5" r="1.5" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M21 15L16 10L5 21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <p className="text-text-muted text-sm tracking-wide">
            {type === 'image' ? 'Preview' : 'Animation Preview'}
          </p>
        </div>
      </div>
    );
  }

  const resolvedUrl = resolveImageUrl(imageUrl);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="relative rounded-2xl overflow-hidden bg-panel-lighter shadow-elegant group">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={resolvedUrl}
          alt="Generated pet character"
          className={`
            w-full h-auto transition-transform duration-700 ease-elegant
            ${type === 'animation' ? '' : 'group-hover:scale-[1.02]'}
          `}
        />

        {/* Subtle overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

        {/* Badge */}
        {type === 'animation' && (
          <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-black/40 backdrop-blur-sm text-[10px] text-white/70 tracking-widest uppercase">
            GIF
          </div>
        )}
      </div>

      {/* Caption */}
      <p className="text-center text-text-muted text-xs mt-4 tracking-wider">
        {type === 'image' ? '角色预览 · Character Preview' : '动画预览 · Animation Preview'}
      </p>
    </div>
  );
}
