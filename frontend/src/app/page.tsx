'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { useStore } from '@/lib/store';

export default function HomePage() {
  const { t } = useI18n();
  const router = useRouter();
  const setCurrentStep = useStore((s) => s.setCurrentStep);
  const reset = useStore((s) => s.reset);

  const handleStart = () => {
    reset();
    setCurrentStep(1);
    router.push('/upload');
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center min-h-[85vh] px-6 text-center overflow-hidden">
        {/* Subtle background grain */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(212,165,116,0.03)_0%,transparent_70%)]" />
        
        {/* Decorative line */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-32 bg-gradient-to-b from-transparent via-accent/20 to-transparent" />

        <div className="relative z-10 max-w-4xl mx-auto space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-border-subtle bg-panel/50 backdrop-blur-sm animate-fade-in">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-gentle-pulse" />
            <span className="text-[11px] text-text-secondary tracking-[0.2em] uppercase">AI-Powered</span>
          </div>

          {/* Title */}
          <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-text-primary leading-[1.1] tracking-tight animate-fade-in-up">
            {t('home.hero.title')}
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl mx-auto text-text-secondary text-base sm:text-lg leading-relaxed tracking-wide animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
            {t('home.hero.subtitle')}
          </p>

          {/* CTA */}
          <div className="pt-4 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <button
              onClick={handleStart}
              className="
                group relative inline-flex items-center gap-3 px-10 py-4 rounded-xl
                bg-accent text-text-inverse text-sm font-medium tracking-wide
                transition-all duration-700 ease-elegant
                hover:shadow-glow hover:scale-[1.02]
                active:scale-[0.98]
              "
            >
              <span>{t('home.hero.cta')}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="transition-transform duration-500 group-hover:translate-x-1">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
          </div>
        </div>

        {/* Bottom decorative element */}
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2">
          <div className="w-px h-16 bg-gradient-to-b from-accent/20 to-transparent animate-shimmer" />
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section header */}
          <div className="text-center mb-20">
            <div className="w-8 h-px bg-accent/30 mx-auto mb-6" />
            <h2 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight">
              {t('home.how.title')}
            </h2>
          </div>

          {/* Steps */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: '01', titleKey: 'home.how.step1', descKey: 'home.how.step1.desc' },
              { step: '02', titleKey: 'home.how.step2', descKey: 'home.how.step2.desc' },
              { step: '03', titleKey: 'home.how.step3', descKey: 'home.how.step3.desc' },
              { step: '04', titleKey: 'home.how.step4', descKey: 'home.how.step4.desc' },
            ].map((item, i) => (
              <div key={item.step} className="group relative">
                <div className="p-6 rounded-2xl bg-panel border border-border-subtle hover:border-border-medium transition-all duration-700">
                  <span className="text-accent/30 font-serif text-5xl block mb-4">{item.step}</span>
                  <h3 className="text-text-primary text-base font-medium tracking-wide mb-2">
                    {t(item.titleKey)}
                  </h3>
                  <p className="text-text-muted text-sm leading-relaxed tracking-wide">
                    {t(item.descKey)}
                  </p>
                </div>
                {/* Connector */}
                {i < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-px bg-border-subtle" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Value Props */}
      <section className="py-32 px-6 border-t border-border-subtle">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            { titleKey: 'home.feature1.title', descKey: 'home.feature1.desc', icon: '◎' },
            { titleKey: 'home.feature2.title', descKey: 'home.feature2.desc', icon: '◈' },
            { titleKey: 'home.feature3.title', descKey: 'home.feature3.desc', icon: '◇' },
            { titleKey: 'home.feature4.title', descKey: 'home.feature4.desc', icon: '◆' },
          ].map((feature) => (
            <div key={feature.titleKey} className="group p-8 rounded-2xl border border-border-subtle hover:border-border-medium transition-all duration-700 bg-panel/30 hover:bg-panel/60">
              <div className="text-accent/40 text-2xl mb-6 transition-colors duration-700 group-hover:text-accent/70">
                {feature.icon}
              </div>
              <h3 className="text-text-primary text-base font-medium tracking-wide mb-3">
                {t(feature.titleKey)}
              </h3>
              <p className="text-text-muted text-sm leading-relaxed tracking-wide">
                {t(feature.descKey)}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-32 px-6 border-t border-border-subtle">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-8 h-px bg-accent/30 mx-auto mb-6" />
            <h2 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight">
              {t('home.testimonial.title')}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              { quoteKey: 'home.testimonial1', authorKey: 'home.testimonial1.author' },
              { quoteKey: 'home.testimonial2', authorKey: 'home.testimonial2.author' },
            ].map((item) => (
              <div key={item.quoteKey} className="p-8 rounded-2xl bg-panel border border-border-subtle">
                <blockquote className="font-serif text-lg text-text-primary/90 leading-relaxed italic mb-6">
                  {t(item.quoteKey)}
                </blockquote>
                <cite className="text-text-muted text-sm tracking-wider not-italic">
                  {t(item.authorKey)}
                </cite>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-6 border-t border-border-subtle">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="font-serif text-3xl sm:text-4xl text-text-primary tracking-tight mb-6">
            {t('common.slogan')}
          </h2>
          <p className="text-text-secondary text-base mb-10 tracking-wide">
            {t('home.hero.subtitle')}
          </p>
          <button
            onClick={handleStart}
            className="
              group inline-flex items-center gap-3 px-10 py-4 rounded-xl
              border border-accent/30 text-accent text-sm font-medium tracking-wide
              transition-all duration-700 ease-elegant
              hover:bg-accent hover:text-text-inverse hover:shadow-glow
              active:scale-[0.98]
            "
          >
            <span>{t('home.hero.cta')}</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="transition-transform duration-500 group-hover:translate-x-1">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </section>
    </div>
  );
}
