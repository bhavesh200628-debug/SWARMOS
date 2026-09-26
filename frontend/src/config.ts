/**
 * Central API and WebSocket Configuration for SWARMOS Command Center
 * Supports production deployments on Vercel, Docker, or custom domains.
 * All URLs are configured via environment variables:
 * - VITE_API_URL: Backend REST API root (e.g. https://api.swarmos.ai)
 * - VITE_WS_URL: Backend WebSocket telemetry stream (e.g. wss://api.swarmos.ai/ws/telemetry)
 * If unset, defaults to same-origin relative URLs.
 */

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_URL || ''
).replace(/\/$/, '');

export const getWebSocketUrl = (): string => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/ws/telemetry`;
};
