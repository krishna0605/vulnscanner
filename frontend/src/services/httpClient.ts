import axios, { AxiosRequestHeaders } from 'axios';

// Resolve API base URL from multiple frontend env conventions (Next.js, Vite, CRA)
const envBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.VITE_API_BASE_URL ||
  process.env.VITE_API_URL ||
  process.env.REACT_APP_API_BASE_URL ||
  process.env.REACT_APP_API_URL;

const toApiV1 = (base?: string): string => {
  let normalized = (base || 'http://127.0.0.1:8000').replace(/\/$/, '');
  // Force IPv4 when a dev env passes localhost to avoid dual-stack quirks
  normalized = normalized.replace(/:\/\/localhost(?![\w\-\.])/i, '://127.0.0.1');
  if (/\/api\/v1$/.test(normalized)) return normalized;
  if (/\/api$/.test(normalized)) return `${normalized}/v1`;
  return `${normalized}/api/v1`;
};

export const API_BASE_URL = toApiV1(envBase);

// Removed unused API_HOST_BASE to satisfy linting rules

// Centralized Axios instance with base URL and interceptors
export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// Attach Authorization from local storage only
http.interceptors.request.use(async (config) => {
  // Use AxiosRequestHeaders union type to handle both plain objects and AxiosHeaders
  const headers: AxiosRequestHeaders = (config.headers as AxiosRequestHeaders) || {};

  // Helper functions to set/get headers regardless of header implementation
  const setHeader = (name: string, value: string) => {
    const h: any = headers as any;
    if (typeof h.set === 'function') {
      h.set(name, value);
    } else {
      (headers as Record<string, string>)[name] = value;
    }
  };
  const getHeader = (name: string): string | undefined => {
    const h: any = headers as any;
    if (typeof h.get === 'function') {
      return h.get(name);
    }
    return (headers as Record<string, string>)[name];
  };

  // Read token from localStorage/sessionStorage
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  if (token) {
    setHeader('Authorization', `Bearer ${token}`);
  }

  // Always accept JSON
  setHeader('Accept', 'application/json');

  // Only set Content-Type for requests with a body
  const method = (config.method || 'get').toUpperCase();
  if (method !== 'GET' && method !== 'HEAD') {
    const existing = getHeader('Content-Type');
    if (!existing) {
      setHeader('Content-Type', 'application/json');
    }
  }

  config.headers = headers;
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    // Pass through errors; callers will handle UX
    return Promise.reject(error);
  }
);

const httpClient = http;
export default httpClient;