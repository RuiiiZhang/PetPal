import type {
  UploadResponse,
  GenerateResponse,
  PaymentResponse,
  DownloadResponse,
  OrderStatusResponse,
  PetStyle,
} from './types';

// ============================================================
// Mock API — full 6-step demo flow with simulated delays
// ============================================================

const MOCK_ORDER_ID = 'petpal-demo-' + Date.now().toString(36);

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Placeholder images (public domain / picsum)
const MOCK_CHARACTER_URL =
  'https://picsum.photos/seed/petpal-char/800/800';
const MOCK_ANIMATION_URL =
  'https://picsum.photos/seed/petpal-anim/800/600';

/**
 * Step 1 — Upload photos
 */
export async function uploadPhotos(
  _photos: File[],
  _petName: string,
  _style: PetStyle
): Promise<UploadResponse> {
  await delay(1500); // simulate upload + breed detection
  return {
    order_id: MOCK_ORDER_ID,
    pet_breed: 'Golden Retriever',
    message: 'Photos uploaded successfully. Breed detected via AI.',
  };
}

/**
 * Step 3 — Generate character image
 */
export async function generateCharacter(_orderId: string): Promise<GenerateResponse> {
  await delay(3000); // simulate AI generation
  return {
    status: 'completed',
    image_url: MOCK_CHARACTER_URL,
    message: 'Character image generated successfully.',
  };
}

/**
 * Step 3b — Confirm character
 */
export async function confirmCharacter(
  _orderId: string,
  _approved: boolean
): Promise<{ status: string; message: string }> {
  await delay(800);
  return { status: 'confirmed', message: 'Character confirmed.' };
}

/**
 * Step 4 — Generate animation
 */
export async function generateAnimation(_orderId: string): Promise<GenerateResponse> {
  await delay(3500); // simulate AI animation generation
  return {
    status: 'completed',
    image_url: MOCK_ANIMATION_URL,
    message: 'Animation generated successfully.',
  };
}

/**
 * Step 4b — Confirm animation
 */
export async function confirmAnimation(
  _orderId: string,
  _approved: boolean
): Promise<{ status: string; message: string }> {
  await delay(800);
  return { status: 'confirmed', message: 'Animation confirmed.' };
}

/**
 * Step 5 — Create payment
 */
export async function createPayment(_orderId: string): Promise<PaymentResponse> {
  await delay(1200);
  return {
    payment_url: '#mock-payment',
    order_id: MOCK_ORDER_ID,
    amount: 29.9,
    message: 'Payment created. (Demo mode — auto-confirmed)',
  };
}

/**
 * Poll order status
 */
export async function getOrderStatus(_orderId: string): Promise<OrderStatusResponse> {
  await delay(500);
  return {
    status: 'completed',
    order_id: MOCK_ORDER_ID,
  };
}

/**
 * Step 6 — Get download links
 */
export async function getDownloadLinks(_orderId: string): Promise<DownloadResponse> {
  await delay(1000);
  return {
    files: [
      {
        name: 'PetPal_Desktop_v1.0.zip',
        url: '#demo-desktop',
        size: '45.2 MB',
        type: 'desktop_pet',
      },
      {
        name: 'PetPal_Stickers_v1.0.zip',
        url: '#demo-stickers',
        size: '12.8 MB',
        type: 'sticker_pack',
      },
      {
        name: 'QuickStart_Guide.pdf',
        url: '#demo-guide',
        size: '1.2 MB',
        type: 'guide',
      },
    ],
    message: 'Download links ready.',
  };
}

/**
 * Helper: resolve image URL (passthrough for absolute URLs)
 */
export function resolveImageUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('#')) {
    return path;
  }
  return path;
}

/**
 * Helper: get the API base URL (unused in mock mode)
 */
export function getApiBaseUrl(): string {
  return 'mock://demo';
}
