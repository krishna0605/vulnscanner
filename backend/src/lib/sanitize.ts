/**
 * Input Sanitization Utilities
 * Prevents injection attacks by sanitizing user inputs
 */

/**
 * Escapes HTML entities to prevent XSS
 */
export function escapeHtml(str: string): string {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Removes potential SQL injection patterns (for logging purposes)
 * Note: This is NOT a replacement for parameterized queries
 */
export function sanitizeForLogging(str: string): string {
  if (!str) return '';
  return str
    .replace(/['";]/g, '')
    .replace(/--/g, '')
    .replace(/\/\*/g, '')
    .replace(/\*\//g, '')
    .replace(/\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|OR|AND)\b/gi, '[FILTERED]');
}

/**
 * Sanitizes user input for safe storage
 * Trims whitespace and removes control characters
 */
export function sanitizeInput(str: string, maxLength: number = 1000): string {
  if (!str) return '';
  return (
    str
      .trim()
      .substring(0, maxLength)
      // Remove control characters except newlines
      .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
  );
}

/**
 * Validates and sanitizes URL input
 */
export function sanitizeUrl(url: string): string | null {
  if (!url) return null;

  try {
    const parsed = new URL(url.trim());

    // Only allow http and https protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return null;
    }

    return parsed.toString();
  } catch {
    return null;
  }
}

/**
 * Sanitizes object properties recursively
 */
export function sanitizeObject<T extends Record<string, unknown>>(obj: T): T {
  const sanitized: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value);
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value as Record<string, unknown>);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized as T;
}
