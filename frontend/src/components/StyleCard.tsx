'use client';

import React from 'react';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';
import type { StyleOption, PetStyle } from '@/lib/types';

const STYLES: StyleOption[] = [
  {
    id: 'cute',
    nameKey: 'style.cute.name',
    descKey: 'style.cute.desc',
    price: 29,
    icon: '◐',
    popular: true,
  },
  {
    id: 'realistic',
    nameKey: 'style.realistic.name',
    descKey: 'style.realistic.desc',
    price: 49,
    icon: '◑',
  },
  {
    id: 'cartoon',
    nameKey: 'style.cartoon.name',
    descKey: 'style.cartoon.desc',
    price: 39,
    icon: '◒',
  },
];

interface StyleCardProps {
  styleOption: StyleOption;
  isSelected: boolean;
  onSelect: (style: PetStyle) => void;
}

export function StyleCard({ styleOption, isSelected, onSelect }: StyleCardProps) {
  const { t } = useI18n();

  return (
    <button
      onClick={() => onSelect(styleOption.id)}
      className={`
        relative w-full text-left rounded-2xl p-8 transition-all duration-700 ease-elegant group
        ${isSelected
          ? 'bg-panel-light border border-accent/30 shadow-glow'
          : 'bg-panel border border-border-subtle hover:border-border-medium hover:bg-panel-light'
        }
      `}
    >
      {/* Popular badge */}
      {styleOption.popular && (
        <div className="absolute -top-2.5 right-6 px-3 py-0.5 rounded-full bg-accent text-text-inverse text-[10px] tracking-widest uppercase font-medium">
          {t('style.popular')}
        </div>
      )}

      {/* Selection indicator */}
      <div className={`
        absolute top-6 left-6 w-5 h-5 rounded-full border-2 transition-all duration-500
        ${isSelected ? 'border-accent bg-accent' : 'border-text-muted/30'}
      `}>
        {isSelected && (
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        )}
      </div>

      {/* Content */}
      <div className="ml-8">
        {/* Icon */}
        <div className={`
          w-14 h-14 rounded-xl flex items-center justify-center mb-5 text-xl transition-all duration-500
          ${isSelected ? 'bg-accent/15 text-accent' : 'bg-panel-lighter text-text-muted group-hover:text-text-secondary'}
        `}>
          {styleOption.icon}
        </div>

        {/* Name */}
        <h3 className={`
          font-serif text-xl mb-2 transition-colors duration-500
          ${isSelected ? 'text-accent' : 'text-text-primary group-hover:text-text-primary'}
        `}>
          {t(styleOption.nameKey)}
        </h3>

        {/* Description */}
        <p className="text-text-secondary text-sm leading-relaxed mb-5">
          {t(styleOption.descKey)}
        </p>

        {/* Price */}
        <div className="flex items-baseline gap-1">
          <span className={`
            text-xs transition-colors duration-500
            ${isSelected ? 'text-accent/60' : 'text-text-muted'}
          `}>
            {t('style.price')}
          </span>
          <span className={`
            font-serif text-2xl transition-colors duration-500
            ${isSelected ? 'text-accent' : 'text-text-primary'}
          `}>
            {styleOption.price}
          </span>
        </div>
      </div>
    </button>
  );
}

export { STYLES };
export default StyleCard;
