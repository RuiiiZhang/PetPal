'use client';

import { create } from 'zustand';
import type { PetPhoto, PetStyle, OrderData, DownloadFile, ToastMessage } from './types';

interface PetPalStore {
  // Order data
  orderId: string | null;
  petName: string;
  photos: PetPhoto[];
  style: PetStyle | null;
  petBreed: string | null;
  characterImageUrl: string | null;
  animationUrl: string | null;
  paymentUrl: string | null;
  paymentStatus: 'unpaid' | 'paid' | 'pending' | null;
  downloadFiles: DownloadFile[] | null;

  // UI state
  isGenerating: boolean;
  currentStep: number;
  toasts: ToastMessage[];

  // Actions
  setOrderId: (id: string) => void;
  setPetName: (name: string) => void;
  addPhotos: (photos: PetPhoto[]) => void;
  removePhoto: (id: string) => void;
  clearPhotos: () => void;
  setStyle: (style: PetStyle) => void;
  setPetBreed: (breed: string) => void;
  setCharacterImageUrl: (url: string) => void;
  setAnimationUrl: (url: string) => void;
  setPaymentUrl: (url: string) => void;
  setPaymentStatus: (status: 'unpaid' | 'paid' | 'pending') => void;
  setDownloadFiles: (files: DownloadFile[]) => void;
  setIsGenerating: (loading: boolean) => void;
  setCurrentStep: (step: number) => void;
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;
  reset: () => void;
}

export const useStore = create<PetPalStore>((set) => ({
  // Initial state
  orderId: null,
  petName: '',
  photos: [],
  style: null,
  petBreed: null,
  characterImageUrl: null,
  animationUrl: null,
  paymentUrl: null,
  paymentStatus: null,
  downloadFiles: null,
  isGenerating: false,
  currentStep: 0,
  toasts: [],

  // Actions
  setOrderId: (id) => set({ orderId: id }),
  setPetName: (name) => set({ petName: name }),
  addPhotos: (newPhotos) =>
    set((state) => ({ photos: [...state.photos, ...newPhotos] })),
  removePhoto: (id) =>
    set((state) => ({
      photos: state.photos.filter((p) => p.id !== id),
    })),
  clearPhotos: () => set({ photos: [] }),
  setStyle: (style) => set({ style }),
  setPetBreed: (breed) => set({ petBreed: breed }),
  setCharacterImageUrl: (url) => set({ characterImageUrl: url }),
  setAnimationUrl: (url) => set({ animationUrl: url }),
  setPaymentUrl: (url) => set({ paymentUrl: url }),
  setPaymentStatus: (status) => set({ paymentStatus: status }),
  setDownloadFiles: (files) => set({ downloadFiles: files }),
  setIsGenerating: (loading) => set({ isGenerating: loading }),
  setCurrentStep: (step) => set({ currentStep: step }),
  addToast: (toast) =>
    set((state) => ({
      toasts: [
        ...state.toasts,
        { ...toast, id: Date.now().toString() + Math.random().toString(36) },
      ],
    })),
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
  reset: () =>
    set({
      orderId: null,
      petName: '',
      photos: [],
      style: null,
      petBreed: null,
      characterImageUrl: null,
      animationUrl: null,
      paymentUrl: null,
      paymentStatus: null,
      downloadFiles: null,
      isGenerating: false,
      currentStep: 0,
    }),
}));
