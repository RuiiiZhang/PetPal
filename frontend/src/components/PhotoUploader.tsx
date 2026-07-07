'use client';

import React, { useCallback, useRef, useState } from 'react';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import type { PetPhoto } from '@/lib/types';

export default function PhotoUploader() {
  const { t } = useI18n();
  const { photos, addPhotos, removePhoto } = useStore();
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateId = () => Date.now().toString(36) + Math.random().toString(36).slice(2);

  const processFiles = useCallback(
    (files: FileList | File[]) => {
      const validFiles = Array.from(files).filter(
        (f) => f.type.startsWith('image/') && f.size <= 10 * 1024 * 1024
      );
      const newPhotos: PetPhoto[] = validFiles.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
        id: generateId(),
      }));
      if (newPhotos.length > 0) {
        addPhotos(newPhotos);
      }
    },
    [addPhotos]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      processFiles(e.dataTransfer.files);
    },
    [processFiles]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        processFiles(e.target.files);
        e.target.value = '';
      }
    },
    [processFiles]
  );

  const handleRemove = useCallback(
    (id: string) => {
      const photo = photos.find((p) => p.id === id);
      if (photo) URL.revokeObjectURL(photo.preview);
      removePhoto(id);
    },
    [photos, removePhoto]
  );

  return (
    <div className="space-y-6">
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          relative cursor-pointer rounded-2xl border transition-all duration-500 ease-elegant
          ${isDragging
            ? 'border-accent bg-accent/5 shadow-glow'
            : 'border-border-medium hover:border-accent/30 bg-panel/50'
          }
        `}
      >
        <div className="flex flex-col items-center justify-center py-16 px-6">
          {/* Upload icon */}
          <div className={`
            w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-all duration-500
            ${isDragging ? 'bg-accent/20 scale-110' : 'bg-panel-lighter'}
          `}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" className={`transition-colors duration-500 ${isDragging ? 'text-accent' : 'text-text-muted'}`}>
              <path d="M21 15V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="17 8 12 3 7 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>

          <p className="text-text-primary text-sm font-medium mb-2 tracking-wide">
            {t('upload.dragDrop')}
          </p>
          <p className="text-text-muted text-xs tracking-wide">
            {t('upload.support')}
          </p>

          {photos.length > 0 && (
            <p className="text-accent/70 text-xs mt-3 tracking-wide">
              {t('upload.photosCount', { count: photos.length })}
            </p>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Multi-photo hint */}
      <p className="text-text-muted text-xs text-center tracking-wider">
        {t('upload.multiHint')}
      </p>

      {/* Photo previews */}
      {photos.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {photos.map((photo, index) => (
            <div
              key={photo.id}
              className="group relative aspect-square rounded-xl overflow-hidden bg-panel-lighter shadow-card hover:shadow-card-hover transition-all duration-500"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={photo.preview}
                alt={t('upload.preview')}
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
              />

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              {/* Remove button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemove(photo.id);
                }}
                className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 hover:bg-accent/80"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>

              {/* Index badge */}
              <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded-full bg-black/50 backdrop-blur-sm text-[10px] text-white/80 tracking-wider">
                {index + 1}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
