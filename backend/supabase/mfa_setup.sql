-- ============================================
-- MFA Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS user_mfa_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- MFA Status
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_type TEXT CHECK (mfa_type IN ('totp', 'email', 'both')) DEFAULT NULL,
    
    -- TOTP Configuration (encrypted)
    totp_secret TEXT,
    totp_verified_at TIMESTAMPTZ,
    
    -- Backup Codes (hashed)
    backup_codes TEXT[],
    backup_codes_generated_at TIMESTAMPTZ,
    backup_codes_used INTEGER DEFAULT 0,
    
    -- Rate Limiting
    failed_attempts INTEGER DEFAULT 0,
    last_failed_at TIMESTAMPTZ,
    locked_until TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT unique_user_mfa UNIQUE(user_id)
);

-- ============================================
-- Email OTP Codes Table
-- ============================================
CREATE TABLE IF NOT EXISTS email_otp_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    code_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_mfa_user_id ON user_mfa_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_otp_user_id ON email_otp_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_otp_expires ON email_otp_codes(expires_at);

-- ============================================
-- Row Level Security
-- ============================================
ALTER TABLE user_mfa_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_otp_codes ENABLE ROW LEVEL SECURITY;

-- Users can only view their own MFA settings
CREATE POLICY "Users can view own MFA settings"
ON user_mfa_settings FOR SELECT
USING (auth.uid() = user_id);

-- Users can update their own MFA settings
CREATE POLICY "Users can update own MFA settings"
ON user_mfa_settings FOR UPDATE
USING (auth.uid() = user_id);

-- Users can insert their own MFA settings
CREATE POLICY "Users can insert own MFA settings"
ON user_mfa_settings FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- OTP codes policies
CREATE POLICY "Users can manage own OTP codes"
ON email_otp_codes FOR ALL
USING (auth.uid() = user_id);

-- ============================================
-- Auto-update timestamp trigger
-- ============================================
CREATE OR REPLACE FUNCTION update_mfa_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS mfa_updated_at ON user_mfa_settings;
CREATE TRIGGER mfa_updated_at
    BEFORE UPDATE ON user_mfa_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_mfa_timestamp();

-- ============================================
-- Cleanup expired OTP codes function
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_expired_otp_codes()
RETURNS void AS $$
BEGIN
    DELETE FROM email_otp_codes WHERE expires_at < now();
END;
$$ LANGUAGE plpgsql;
