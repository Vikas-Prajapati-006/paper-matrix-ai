import FingerprintJS from '@fingerprintjs/fingerprintjs';

const BACKEND_URL = import.meta.env.PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface QuotaStatus {
  remaining: number;
  total: number;
  resets_in_seconds?: number;
}

/**
 * Initializes and retrieves or creates a persistent visitor hardware hash.
 */
export async function getDeviceFingerprint(): Promise<string> {
  const cached = localStorage.getItem('pm_device_id');
  if (cached) {
    return cached;
  }

  try {
    const fp = await FingerprintJS.load();
    const result = await fp.get();
    const visitorId = result.visitorId;
    localStorage.setItem('pm_device_id', visitorId);
    return visitorId;
  } catch (err) {
    console.warn('FingerprintJS fallback to random token:', err);
    const fallbackId = 'dev_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('pm_device_id', fallbackId);
    return fallbackId;
  }
}

/**
 * Pings backend to check live quota credits for the detected fingerprint.
 */
export async function fetchQuotaStatus(): Promise<QuotaStatus> {
  const deviceId = await getDeviceFingerprint();
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/quota/${deviceId}`);
    if (!response.ok) {
      throw new Error(`Quota check failed with status: ${response.status}`);
    }
    const data = await response.json();
    return {
      remaining: data.remaining_credits ?? 3,
      total: data.total_quota ?? 3,
      resets_in_seconds: data.ttl_seconds ?? 0,
    };
  } catch (error) {
    console.error('Failed to retrieve quota status:', error);
    return { remaining: 3, total: 3 };
  }
}