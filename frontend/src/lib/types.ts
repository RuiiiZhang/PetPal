// PetPal TypeScript Type Definitions

export interface PetPhoto {
  file: File;
  preview: string;
  id: string;
}

export type PetStyle = 'cute' | 'realistic' | 'cartoon';

export interface StyleOption {
  id: PetStyle;
  nameKey: string;
  descKey: string;
  price: number;
  icon: string;
  popular?: boolean;
}

export interface OrderData {
  order_id: string | null;
  pet_name: string;
  photos: PetPhoto[];
  style: PetStyle | null;
  pet_breed: string | null;
  character_image_url: string | null;
  animation_url: string | null;
  payment_url: string | null;
  payment_status: 'unpaid' | 'paid' | 'pending' | null;
  download_urls: DownloadFile[] | null;
  created_at: string | null;
}

export interface DownloadFile {
  name: string;
  url: string;
  size: string;
  type: 'desktop_pet' | 'sticker_pack' | 'guide';
}

export interface UploadResponse {
  order_id: string;
  pet_breed: string;
  message: string;
}

export interface GenerateResponse {
  status: string;
  image_url: string;
  message: string;
}

export interface PaymentResponse {
  payment_url: string;
  order_id: string;
  amount: number;
  message: string;
}

export interface DownloadResponse {
  files: DownloadFile[];
  message: string;
}

export interface OrderStatusResponse {
  status: 'uploading' | 'processing' | 'character_ready' | 'animation_ready' | 'paid' | 'completed';
  order_id: string;
}

export type Locale = 'zh' | 'en';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}
