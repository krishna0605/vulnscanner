import { URL } from 'url';

/**
 * URL normalizer for consistent URL handling and deduplication.
 * Ported from legacy normalizer.py
 */
export class URLNormalizer {
  private excludedExtensions: Set<string>;
  private trackingParams: Set<string>;

  constructor() {
    this.excludedExtensions = new Set([
      // Images
      '.jpg',
      '.jpeg',
      '.png',
      '.gif',
      '.bmp',
      '.svg',
      '.webp',
      '.ico',
      // Documents
      '.pdf',
      '.doc',
      '.docx',
      '.xls',
      '.xlsx',
      '.ppt',
      '.pptx',
      // Archives
      '.zip',
      '.rar',
      '.tar',
      '.gz',
      '.7z',
      // Media
      '.mp3',
      '.mp4',
      '.avi',
      '.mov',
      '.wmv',
      '.flv',
      // Other
      '.exe',
      '.dmg',
      '.pkg',
      '.deb',
      '.rpm',
      '.css', // Added css
    ]);

    this.trackingParams = new Set([
      'utm_source',
      'utm_medium',
      'utm_campaign',
      'utm_term',
      'utm_content',
      'gclid',
      'fbclid',
      'msclkid',
      '_ga',
      '_gid',
      'ref',
      'referrer',
    ]);
  }

  /**
   * Normalize a URL for consistent handling.
   */
  normalizeUrl(url: string): string {
    try {
      const parsed = new URL(url.trim());

      // Normalize to lowercase
      parsed.protocol = parsed.protocol.toLowerCase();
      parsed.hostname = parsed.hostname.toLowerCase();

      // Remove default ports
      if (parsed.port === '80' && parsed.protocol === 'http:') {
        parsed.port = '';
      } else if (parsed.port === '443' && parsed.protocol === 'https:') {
        parsed.port = '';
      }

      // Normalize path
      parsed.pathname = this._normalizePath(parsed.pathname);

      // Normalize search params
      this._normalizeSearchParams(parsed.searchParams);

      // Remove hash
      parsed.hash = '';

      return parsed.toString();
    } catch (e) {
      // Return original if parsing fails (e.g. relative URLs)
      return url;
    }
  }

  private _normalizePath(path: string): string {
    if (!path || path === '/') return '/';

    // Remove trailing slash
    if (path.length > 1 && path.endsWith('/')) {
      path = path.slice(0, -1);
    }

    // Ensure starts with /
    if (!path.startsWith('/')) {
      path = '/' + path;
    }

    return path;
  }

  private _normalizeSearchParams(params: URLSearchParams) {
    // Remove tracking params
    const keys = Array.from(params.keys());
    for (const key of keys) {
      if (this.trackingParams.has(key.toLowerCase())) {
        params.delete(key);
      }
    }

    // Sort params for consistency
    params.sort();
  }

  /**
   * Check if URL is valid for crawling using Playwright
   */
  isValidUrl(url: string): boolean {
    try {
      const parsed = new URL(url);

      // Only HTTP/HTTPS
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return false;
      }

      // Check extensions
      const path = parsed.pathname.toLowerCase();
      for (const ext of this.excludedExtensions) {
        if (path.endsWith(ext)) {
          return false;
        }
      }

      // Check length
      if (url.length > 2000) return false;

      return true;
    } catch (e) {
      return false;
    }
  }

  extractDomain(url: string): string {
    try {
      return new URL(url).hostname;
    } catch {
      return '';
    }
  }

  isSameDomain(url1: string, url2: string): boolean {
    return this.extractDomain(url1) === this.extractDomain(url2);
  }

  deduplicateUrls(urls: string[]): string[] {
    const seen = new Set<string>();
    const unique: string[] = [];

    for (const url of urls) {
      const normalized = this.normalizeUrl(url);
      if (!seen.has(normalized) && this.isValidUrl(normalized)) {
        seen.add(normalized);
        unique.push(normalized);
      }
    }
    return unique;
  }
}
