import { FastifyInstance } from 'fastify';
import { authenticator } from '@otplib/preset-default';
import QRCode from 'qrcode';
import crypto from 'crypto';
import { supabase } from '../lib/supabase';
import { z } from 'zod';
import { success } from '../lib/response';
import { AppError, DatabaseError } from '../lib/errors';

// Validation schemas
const verifyCodeSchema = z.object({
  code: z.string().length(6).regex(/^\d+$/, 'Code must be 6 digits'),
});

const challengeSchema = z.object({
  code: z.string().min(6),
  type: z.enum(['totp', 'backup', 'email']),
});

// Encryption helpers (using AES-256-GCM)
const ENCRYPTION_KEY = process.env.MFA_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
const ALGORITHM = 'aes-256-gcm';

function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const key = Buffer.from(ENCRYPTION_KEY.slice(0, 64), 'hex');
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
  
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  const authTag = cipher.getAuthTag();
  
  return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
}

function decrypt(encryptedData: string): string {
  const [ivHex, authTagHex, encrypted] = encryptedData.split(':');
  const iv = Buffer.from(ivHex, 'hex');
  const authTag = Buffer.from(authTagHex, 'hex');
  const key = Buffer.from(ENCRYPTION_KEY.slice(0, 64), 'hex');
  
  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
  decipher.setAuthTag(authTag);
  
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

// Hash backup codes with bcrypt-like approach (using SHA-256 for simplicity)
function hashCode(code: string): string {
  return crypto.createHash('sha256').update(code).digest('hex');
}

// Generate backup codes
function generateBackupCodes(count: number = 8): string[] {
  const codes: string[] = [];
  for (let i = 0; i < count; i++) {
    // Generate 8-character alphanumeric codes
    const code = crypto.randomBytes(4).toString('hex').toUpperCase();
    codes.push(code);
  }
  return codes;
}

// Rate limiting check
async function checkRateLimit(userId: string): Promise<{ isLocked: boolean; remainingTime?: number }> {
  const { data } = await supabase
    .from('user_mfa_settings')
    .select('failed_attempts, locked_until')
    .eq('user_id', userId)
    .single();

  if (!data) return { isLocked: false };

  if (data.locked_until && new Date(data.locked_until) > new Date()) {
    const remainingTime = Math.ceil((new Date(data.locked_until).getTime() - Date.now()) / 1000);
    return { isLocked: true, remainingTime };
  }

  return { isLocked: false };
}

// Record attempt (success or failure)
async function recordAttempt(userId: string, isSuccess: boolean): Promise<void> {
  if (isSuccess) {
    await supabase
      .from('user_mfa_settings')
      .update({ failed_attempts: 0, locked_until: null, last_failed_at: null })
      .eq('user_id', userId);
  } else {
    const { data } = await supabase
      .from('user_mfa_settings')
      .select('failed_attempts')
      .eq('user_id', userId)
      .single();

    const newAttempts = (data?.failed_attempts || 0) + 1;
    const lockUntil = newAttempts >= 5 
      ? new Date(Date.now() + 15 * 60 * 1000).toISOString() // 15 min lockout
      : null;

    await supabase
      .from('user_mfa_settings')
      .update({ 
        failed_attempts: newAttempts, 
        last_failed_at: new Date().toISOString(),
        locked_until: lockUntil
      })
      .eq('user_id', userId);
  }
}

export async function mfaRoutes(fastify: FastifyInstance) {
  // GET /mfa/status - Get current MFA status for user
  fastify.get('/mfa/status', async (request, reply) => {
    const userId = request.user!.id;

    const { data, error } = await supabase
      .from('user_mfa_settings')
      .select('mfa_enabled, mfa_type, totp_verified_at, created_at, updated_at')
      .eq('user_id', userId)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows
      throw new DatabaseError(error.message);
    }

    const mfaEnabled = data?.mfa_enabled || false;
    
    return success({
      mfaEnabled,
      mfaType: data?.mfa_type || null,
      setupAt: data?.totp_verified_at || data?.created_at || null,
      // If no MFA configured, suggest email OTP for login verification
      suggestEmailOtp: !mfaEnabled,
    });
  });

  // POST /mfa/setup - Generate TOTP secret and QR code
  fastify.post('/mfa/setup', async (request, reply) => {
    const userId = request.user!.id;
    const email = request.user!.email || 'user';

    console.log('[MFA Setup] Starting setup for user:', userId);

    try {
      // Check if MFA is already enabled
      const { data: existing, error: fetchError } = await supabase
        .from('user_mfa_settings')
        .select('mfa_enabled')
        .eq('user_id', userId)
        .single();

      console.log('[MFA Setup] Existing settings:', existing, 'Error:', fetchError?.message);

      if (existing?.mfa_enabled) {
        throw new AppError('MFA is already enabled. Disable it first to set up again.', 400, 'MFA_ALREADY_ENABLED');
      }

      // Generate new secret
      console.log('[MFA Setup] Generating secret...');
      const secret = authenticator.generateSecret();
      
      // Generate QR code
      console.log('[MFA Setup] Generating QR code...');
      const otpauth = authenticator.keyuri(email, 'VulnScanner', secret);
      const qrCodeDataUrl = await QRCode.toDataURL(otpauth);

      // Store encrypted secret (pending verification)
      console.log('[MFA Setup] Encrypting secret...');
      const encryptedSecret = encrypt(secret);
      
      console.log('[MFA Setup] Saving to database...');
      const { error } = await supabase
        .from('user_mfa_settings')
        .upsert({
          user_id: userId,
          totp_secret: encryptedSecret,
          mfa_enabled: false,
          mfa_type: null,
        }, { onConflict: 'user_id' });

      if (error) {
        console.error('[MFA Setup] Database error:', error.message);
        throw new DatabaseError(error.message);
      }

      console.log('[MFA Setup] Success!');
      return success({
        qrCode: qrCodeDataUrl,
        secret: secret, // For manual entry (show only once)
        message: 'Scan QR code with your authenticator app, then verify with a code',
      });
    } catch (err: any) {
      console.error('[MFA Setup] Error:', err.message, err.stack);
      throw err;
    }
  });

  // POST /mfa/verify - Verify TOTP during setup to enable MFA
  fastify.post('/mfa/verify', async (request, reply) => {
    const userId = request.user!.id;
    const { code } = verifyCodeSchema.parse(request.body);

    const { data: settings, error } = await supabase
      .from('user_mfa_settings')
      .select('totp_secret, mfa_enabled')
      .eq('user_id', userId)
      .single();

    if (error || !settings?.totp_secret) {
      throw new AppError('No MFA setup in progress. Please start setup first.', 400, 'NO_MFA_SETUP');
    }

    if (settings.mfa_enabled) {
      throw new AppError('MFA is already enabled.', 400, 'MFA_ALREADY_ENABLED');
    }

    // Decrypt and verify
    const secret = decrypt(settings.totp_secret);
    const isValid = authenticator.verify({ token: code, secret });

    if (!isValid) {
      throw new AppError('Invalid verification code. Please try again.', 400, 'INVALID_CODE');
    }

    // Generate backup codes
    const backupCodes = generateBackupCodes(8);
    const hashedCodes = backupCodes.map(c => hashCode(c));

    // Enable MFA
    const { error: updateError } = await supabase
      .from('user_mfa_settings')
      .update({
        mfa_enabled: true,
        mfa_type: 'totp',
        totp_verified_at: new Date().toISOString(),
        backup_codes: hashedCodes,
        backup_codes_generated_at: new Date().toISOString(),
        failed_attempts: 0,
      })
      .eq('user_id', userId);

    if (updateError) throw new DatabaseError(updateError.message);

    return success({
      enabled: true,
      backupCodes: backupCodes, // Show only once!
      message: 'Two-factor authentication enabled. Save your backup codes in a safe place.',
    });
  });

  // POST /mfa/challenge - Verify code during login
  fastify.post('/mfa/challenge', async (request, reply) => {
    const userId = request.user!.id;
    const { code, type } = challengeSchema.parse(request.body);

    // Rate limiting check
    const rateLimit = await checkRateLimit(userId);
    if (rateLimit.isLocked) {
      throw new AppError(
        `Too many attempts. Try again in ${rateLimit.remainingTime} seconds.`,
        429,
        'RATE_LIMITED'
      );
    }

    const { data: settings, error } = await supabase
      .from('user_mfa_settings')
      .select('totp_secret, backup_codes, mfa_enabled')
      .eq('user_id', userId)
      .single();

    // For TOTP and backup codes, MFA must be enabled
    // For email verification, we allow it even if MFA is not enabled (for login verification)
    if (type !== 'email' && (error || !settings?.mfa_enabled)) {
      throw new AppError('MFA is not enabled for this account.', 400, 'MFA_NOT_ENABLED');
    }

    let isValid = false;

    if (type === 'totp') {
      if (!settings?.totp_secret) {
        throw new AppError('TOTP is not configured.', 400, 'TOTP_NOT_CONFIGURED');
      }
      const secret = decrypt(settings.totp_secret);
      isValid = authenticator.verify({ token: code, secret });
    } else if (type === 'backup') {
      if (!settings?.backup_codes) {
        throw new AppError('No backup codes available.', 400, 'NO_BACKUP_CODES');
      }
      const codeHash = hashCode(code.toUpperCase());
      const backupCodes = settings.backup_codes || [];
      const codeIndex = backupCodes.indexOf(codeHash);
      
      if (codeIndex !== -1) {
        isValid = true;
        // Remove used backup code
        backupCodes.splice(codeIndex, 1);
        await supabase
          .from('user_mfa_settings')
          .update({ 
            backup_codes: backupCodes,
            backup_codes_used: (settings as any).backup_codes_used + 1
          })
          .eq('user_id', userId);
      }
    } else if (type === 'email') {
      // Check email OTP
      const { data: otpData } = await supabase
        .from('email_otp_codes')
        .select('id, code_hash, expires_at, used')
        .eq('user_id', userId)
        .eq('used', false)
        .gt('expires_at', new Date().toISOString())
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (otpData && otpData.code_hash === hashCode(code)) {
        isValid = true;
        // Mark as used
        await supabase
          .from('email_otp_codes')
          .update({ used: true })
          .eq('id', otpData.id);
      }
    }

    // Record the attempt
    await recordAttempt(userId, isValid);

    if (!isValid) {
      throw new AppError('Invalid code. Please try again.', 400, 'INVALID_CODE');
    }

    return success({ verified: true });
  });

  // POST /mfa/disable - Disable MFA (requires current code)
  fastify.post('/mfa/disable', async (request, reply) => {
    const userId = request.user!.id;
    const { code } = verifyCodeSchema.parse(request.body);

    const { data: settings, error } = await supabase
      .from('user_mfa_settings')
      .select('totp_secret, mfa_enabled')
      .eq('user_id', userId)
      .single();

    if (error || !settings?.mfa_enabled) {
      throw new AppError('MFA is not enabled.', 400, 'MFA_NOT_ENABLED');
    }

    // Verify current code before disabling
    const secret = decrypt(settings.totp_secret);
    const isValid = authenticator.verify({ token: code, secret });

    if (!isValid) {
      throw new AppError('Invalid code. Cannot disable MFA.', 400, 'INVALID_CODE');
    }

    // Disable MFA
    const { error: updateError } = await supabase
      .from('user_mfa_settings')
      .update({
        mfa_enabled: false,
        mfa_type: null,
        totp_secret: null,
        backup_codes: null,
      })
      .eq('user_id', userId);

    if (updateError) throw new DatabaseError(updateError.message);

    return success({ disabled: true, message: 'Two-factor authentication disabled.' });
  });

  // POST /mfa/backup-codes - Generate new backup codes
  fastify.post('/mfa/backup-codes', async (request, reply) => {
    const userId = request.user!.id;
    const { code } = verifyCodeSchema.parse(request.body);

    const { data: settings, error } = await supabase
      .from('user_mfa_settings')
      .select('totp_secret, mfa_enabled')
      .eq('user_id', userId)
      .single();

    if (error || !settings?.mfa_enabled) {
      throw new AppError('MFA is not enabled.', 400, 'MFA_NOT_ENABLED');
    }

    // Verify current TOTP code
    const secret = decrypt(settings.totp_secret);
    const isValid = authenticator.verify({ token: code, secret });

    if (!isValid) {
      throw new AppError('Invalid code.', 400, 'INVALID_CODE');
    }

    // Generate new backup codes
    const backupCodes = generateBackupCodes(8);
    const hashedCodes = backupCodes.map(c => hashCode(c));

    const { error: updateError } = await supabase
      .from('user_mfa_settings')
      .update({
        backup_codes: hashedCodes,
        backup_codes_generated_at: new Date().toISOString(),
        backup_codes_used: 0,
      })
      .eq('user_id', userId);

    if (updateError) throw new DatabaseError(updateError.message);

    return success({
      backupCodes: backupCodes,
      message: 'New backup codes generated. Save them in a safe place.',
    });
  });

  // POST /mfa/send-email-otp - Send OTP via email
  fastify.post('/mfa/send-email-otp', async (request, reply) => {
    const userId = request.user!.id;
    const email = request.user!.email;

    if (!email) {
      throw new AppError('No email associated with this account.', 400, 'NO_EMAIL');
    }

    // Generate 6-digit OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    // Delete any existing unused OTP codes for this user
    await supabase
      .from('email_otp_codes')
      .delete()
      .eq('user_id', userId)
      .eq('used', false);

    // Store hashed OTP
    const { error } = await supabase
      .from('email_otp_codes')
      .insert({
        user_id: userId,
        code_hash: hashCode(otp),
        expires_at: expiresAt.toISOString(),
      });

    if (error) throw new DatabaseError(error.message);

    // Send email
    const maskedEmail = email.replace(/(.{2})(.*)(@.*)/, '$1***$3');
    let emailSent = false;

    // Try to send via Resend if API key is configured
    if (process.env.RESEND_API_KEY) {
      try {
        const response = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: process.env.RESEND_FROM_EMAIL || 'VulnScanner <onboarding@resend.dev>',
            to: email,
            subject: 'Your VulnScanner Verification Code',
            html: `
              <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">Your Verification Code</h2>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                  <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #06b6d4;">${otp}</span>
                </div>
                <p style="color: #666;">This code expires in 10 minutes.</p>
                <p style="color: #999; font-size: 12px;">If you didn't request this code, please ignore this email.</p>
              </div>
            `,
          }),
        });
        
        if (response.ok) {
          emailSent = true;
          request.log.info({ email: maskedEmail }, 'OTP email sent via Resend');
        } else {
          const errorData = await response.json();
          request.log.error({ error: errorData }, 'Failed to send email via Resend');
        }
      } catch (err) {
        request.log.error({ err }, 'Error sending email via Resend');
      }
    }

    // For development: Log the OTP to console
    if (!emailSent) {
      request.log.info('========================================');
      request.log.info(`📧 EMAIL OTP for ${email}: ${otp}`);
      request.log.info('========================================');
    }

    return success({
      sent: true,
      message: `Verification code sent to ${maskedEmail}`,
      expiresIn: 600, // 10 minutes in seconds
      // DEV ONLY: Include OTP in response for testing when no email service
      ...(process.env.NODE_ENV === 'development' && !emailSent && { _devOtp: otp }),
    });
  });
}
