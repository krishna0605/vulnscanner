'use client';

import { createClient } from '@/utils/supabase/client';
import { logger } from '@/utils/logger';

export interface ProfileData {
  full_name: string | null;
  bio: string | null;
  avatar_url: string | null;
}

export async function getProfile(userId: string): Promise<ProfileData | null> {
  const supabase = createClient();

  const { data, error } = await supabase
    .from('profiles')
    .select('full_name, bio, avatar_url')
    .eq('id', userId)
    .single();

  if (error) {
    logger.error('Error fetching profile:', { error });
    return null;
  }

  return data;
}

export async function updateProfile(userId: string, data: Partial<ProfileData>): Promise<boolean> {
  const supabase = createClient();

  const { error } = await supabase.from('profiles').upsert({
    id: userId,
    ...data,
    updated_at: new Date().toISOString(),
  });

  if (error) {
    logger.error('Error updating profile:', { error });
    return false;
  }

  return true;
}

export async function uploadAvatar(userId: string, file: File): Promise<string | null> {
  const supabase = createClient();

  // Delete old avatar first
  const { data: existingFiles } = await supabase.storage.from('avatars').list(userId);

  if (existingFiles && existingFiles.length > 0) {
    const filesToDelete = existingFiles.map((f) => `${userId}/${f.name}`);
    await supabase.storage.from('avatars').remove(filesToDelete);
  }

  // Upload new avatar
  const fileExt = file.name.split('.').pop();
  const fileName = `${userId}/avatar.${fileExt}`;

  const { error: uploadError } = await supabase.storage
    .from('avatars')
    .upload(fileName, file, { upsert: true });

  if (uploadError) {
    logger.error('Error uploading avatar:', { error: uploadError });
    return null;
  }

  // Get public URL
  const { data: urlData } = supabase.storage.from('avatars').getPublicUrl(fileName);

  // Update profile with avatar URL
  await updateProfile(userId, { avatar_url: urlData.publicUrl });

  return urlData.publicUrl;
}

export async function deleteAvatar(userId: string): Promise<boolean> {
  const supabase = createClient();

  // List and delete all files in user's folder
  const { data: existingFiles } = await supabase.storage.from('avatars').list(userId);

  if (existingFiles && existingFiles.length > 0) {
    const filesToDelete = existingFiles.map((f) => `${userId}/${f.name}`);
    await supabase.storage.from('avatars').remove(filesToDelete);
  }

  // Clear avatar_url in profile
  await updateProfile(userId, { avatar_url: null });

  return true;
}

export async function exportUserData(userId: string): Promise<object> {
  const supabase = createClient();

  // Fetch all user data
  const [profileRes, projectsRes] = await Promise.all([
    supabase.from('profiles').select('*').eq('id', userId).single(),
    supabase.from('projects').select('*').eq('user_id', userId),
  ]);

  const projectIds = projectsRes.data?.map((p) => p.id) || [];

  let scans: any[] = [];
  let findings: any[] = [];

  if (projectIds.length > 0) {
    const scansRes = await supabase.from('scans').select('*').in('project_id', projectIds);
    scans = scansRes.data || [];

    const scanIds = scans.map((s) => s.id);
    if (scanIds.length > 0) {
      const findingsRes = await supabase.from('findings').select('*').in('scan_id', scanIds);
      findings = findingsRes.data || [];
    }
  }

  return {
    exportedAt: new Date().toISOString(),
    profile: profileRes.data,
    projects: projectsRes.data || [],
    scans,
    findings,
  };
}
