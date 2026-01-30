-- Create scan_profiles table
CREATE TABLE IF NOT EXISTS scan_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  config JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default profiles
INSERT INTO scan_profiles (name, description, config) VALUES
('Quick Scan', 'Fast scan checking headers and basic info only.', '{
  "scanType": "quick",
  "maxDepth": 0,
  "maxPages": 10,
  "checkHeaders": true,
  "checkMixedContent": false,
  "checkComments": false,
  "checkRobots": true
}'),
('Standard Scan', 'Balanced scan (Depth 2, 50 pages) with common vulnerability checks.', '{
  "scanType": "standard",
  "maxDepth": 2,
  "maxPages": 50,
  "checkHeaders": true,
  "checkMixedContent": true,
  "checkComments": true,
  "checkRobots": true,
  "vectorSQLi": true,
  "vectorXSS": true,
  "vectorMisconfig": true
}'),
('Deep Scan', 'Aggressive scan (Depth 3, 200 pages) including all vectors and concurrency.', '{
  "scanType": "deep",
  "maxDepth": 3,
  "maxPages": 200,
  "checkHeaders": true,
  "checkMixedContent": true,
  "checkComments": true,
  "checkRobots": true,
  "vectorSQLi": true,
  "vectorXSS": true,
  "vectorSSRF": true,
  "vectorMisconfig": true,
  "concurrency": 3,
  "rateLimit": 10
}')
ON CONFLICT DO NOTHING;
