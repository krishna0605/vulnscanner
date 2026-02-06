import { createClient } from '@/utils/supabase/server';
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:3001';

async function getAuthToken() {
  const supabase = createClient();
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error) {
    console.error('[MFA Setup] Session error:', error.message);
  }
  console.log('[MFA Setup] Session exists:', !!session);
  return session?.access_token;
}

export async function GET() {
  const token = await getAuthToken();
  
  if (!token) {
    console.log('[MFA Setup GET] No auth token');
    return NextResponse.json({ error: { message: 'Unauthorized' } }, { status: 401 });
  }

  try {
    console.log('[MFA Setup GET] Fetching status from:', `${BACKEND_URL}/mfa/status`);
    const response = await fetch(`${BACKEND_URL}/mfa/status`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    console.log('[MFA Setup GET] Response:', response.status, data);
    return NextResponse.json(data, { status: response.status });
  } catch (error: any) {
    console.error('[MFA Setup GET] Error:', error.message);
    return NextResponse.json({ error: { message: 'Failed to fetch MFA status' } }, { status: 500 });
  }
}

export async function POST() {
  const token = await getAuthToken();
  
  if (!token) {
    console.log('[MFA Setup POST] No auth token');
    return NextResponse.json({ error: { message: 'Unauthorized - Please log in first' } }, { status: 401 });
  }

  try {
    console.log('[MFA Setup POST] Calling backend:', `${BACKEND_URL}/mfa/setup`);
    const response = await fetch(`${BACKEND_URL}/mfa/setup`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    const data = await response.json();
    console.log('[MFA Setup POST] Backend response:', response.status, JSON.stringify(data).slice(0, 200));
    return NextResponse.json(data, { status: response.status });
  } catch (error: any) {
    console.error('[MFA Setup POST] Error:', error.message);
    return NextResponse.json({ error: { message: `Failed to setup MFA: ${error.message}` } }, { status: 500 });
  }
}
