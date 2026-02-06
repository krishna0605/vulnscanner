import { NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:3001';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/dashboard';

  console.log('[Callback] Received code:', code ? 'yes' : 'no');

  if (code) {
    const supabase = createClient();
    const { data, error } = await supabase.auth.exchangeCodeForSession(code);
    
    console.log('[Callback] Exchange result:', { error: error?.message, hasSession: !!data?.session });
    
    if (!error && data?.session) {
      // Get the session to check MFA status
      const session = data.session;
      
      if (session?.access_token) {
        try {
          // Check MFA status from backend
          console.log('[Callback] Checking MFA status...');
          const mfaResponse = await fetch(`${BACKEND_URL}/mfa/status`, {
            headers: {
              'Authorization': `Bearer ${session.access_token}`,
              'Content-Type': 'application/json',
            },
          });
          
          console.log('[Callback] MFA response status:', mfaResponse.status);
          
          if (mfaResponse.ok) {
            const mfaData = await mfaResponse.json();
            console.log('[Callback] MFA data:', mfaData);
            
            if (mfaData.data?.mfaEnabled) {
              // User has MFA enabled - redirect to verification
              const mfaType = mfaData.data.mfaType || 'totp';
              console.log('[Callback] MFA enabled, redirecting to verify-2fa with mode:', mfaType);
              return getRedirectResponse(request, origin, `/verify-2fa?mode=${mfaType}`);
            } else {
              // No MFA configured - auto-send email OTP for verification
              console.log('[Callback] No MFA, sending email OTP for verification');
              await fetch(`${BACKEND_URL}/mfa/send-email-otp`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${session.access_token}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({}),
              });
              return getRedirectResponse(request, origin, '/verify-2fa?mode=email_verify');
            }
          }
        } catch (err) {
          console.error('[Callback] Error checking MFA status:', err);
          // On error, proceed to dashboard (fail open for now)
        }
      }
      
      // Fallback: redirect to dashboard
      console.log('[Callback] Fallback: redirecting to dashboard');
      return getRedirectResponse(request, origin, next);
    }
    
    // Log the specific error
    console.error('[Callback] Auth error:', error?.message);
  }

  // Return the user to login with error message
  return NextResponse.redirect(`${origin}/login?error=auth_callback_error`);
}

function getRedirectResponse(request: Request, origin: string, path: string) {
  const forwardedHost = request.headers.get('x-forwarded-host');
  const isLocalEnv = process.env.NODE_ENV === 'development';
  
  if (isLocalEnv) {
    return NextResponse.redirect(`${origin}${path}`);
  } else if (forwardedHost) {
    return NextResponse.redirect(`https://${forwardedHost}${path}`);
  } else {
    return NextResponse.redirect(`${origin}${path}`);
  }
}
