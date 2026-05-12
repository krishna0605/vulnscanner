'use client';

import { logger } from '@/utils/logger';

export interface ProfileData {
  full_name: string | null;
  bio: string | null;
  avatar_url: string | null;
}

export async function getProfile(userId: string): Promise<ProfileData | null> {
  return readProfile(userId);
}

export async function updateProfile(userId: string, data: Partial<ProfileData>): Promise<boolean> {
  try {
    const existing = readProfile(userId) ?? { full_name: null, bio: null, avatar_url: null };
    writeProfile(userId, { ...existing, ...data });
    return true;
  } catch (error) {
    logger.error('Error updating profile:', { error });
    return false;
  }
}

export async function uploadAvatar(userId: string, file: File): Promise<string | null> {
  try {
    const dataUrl = await fileToDataUrl(file);
    await updateProfile(userId, { avatar_url: dataUrl });
    return dataUrl;
  } catch (error) {
    logger.error('Error uploading avatar:', { error });
    return null;
  }
}

export async function deleteAvatar(userId: string): Promise<boolean> {
  return updateProfile(userId, { avatar_url: null });
}

export async function exportUserData(userId: string): Promise<object> {
  return {
    exportedAt: new Date().toISOString(),
    profile: readProfile(userId),
    projects: [],
    scans: [],
    findings: [],
  };
}

function readProfile(userId: string): ProfileData | null {
  if (typeof window === 'undefined') return null;
  const raw = window.localStorage.getItem(profileKey(userId));
  return raw ? (JSON.parse(raw) as ProfileData) : null;
}

function writeProfile(userId: string, data: ProfileData) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(profileKey(userId), JSON.stringify(data));
}

function profileKey(userId: string) {
  return `vulnscanner:profile:${userId}`;
}

function fileToDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
