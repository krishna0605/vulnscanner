import httpClient, { API_BASE_URL } from './httpClient.ts';

// Types for backend responses
export interface UserPublic {
  id: string;
  email: string;
  username?: string | null;
  full_name?: string | null;
  role?: string | null;
  is_active?: boolean;
  email_verified?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserPublic;
  expires_in?: number;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await httpClient.post<LoginResponse>(`${API_BASE_URL}/auth/login`, { email, password });
  return data;
}

export async function register(email: string, password: string, fullName?: string): Promise<LoginResponse> {
  // Backend expects 'full_name' field
  const payload: Record<string, any> = { email, password };
  if (fullName) payload.full_name = fullName;
  const { data } = await httpClient.post<LoginResponse>(`${API_BASE_URL}/auth/register`, payload);
  return data;
}

export async function getCurrentUser(): Promise<UserPublic> {
  const { data } = await httpClient.get<UserPublic>(`${API_BASE_URL}/users/me`);
  return data;
}