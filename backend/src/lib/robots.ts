import robotsParser from 'robots-parser';
import { URL } from 'url';

interface RobotsCacheItem {
  parser: any;
  expiresAt: number;
}

export class RobotsService {
  private cache = new Map<string, RobotsCacheItem>();
  private readonly TTL_MS = 15 * 60 * 1000; // 15 minutes
  private readonly MAX_CACHE_SIZE = 256;

  constructor() {}

  /**
   * Check if a URL is allowed to be crawled.
   * If robots.txt check fails (network error etc), we default to Allow (compliant with standard practice).
   */
  async isAllowed(url: string, userAgent: string = '*'): Promise<boolean> {
    try {
      const parsedUrl = new URL(url);
      const origin = parsedUrl.origin;
      const robotsUrl = `${origin}/robots.txt`;

      let parser = this.getCachedParser(origin);

      if (!parser) {
        try {
          // Fetch robots.txt
          const response = await fetch(robotsUrl, {
            method: 'GET',
            headers: { 'User-Agent': userAgent },
            signal: AbortSignal.timeout(5000), // 5s timeout
          });

          let content = '';
          if (response.status === 200) {
            content = await response.text();
          } else {
            // If 404 or other error, assume allowed (empty content)
            content = '';
          }

          // Initialize parser
          parser = robotsParser(robotsUrl, content);
          this.setCachedParser(origin, parser);
        } catch (err) {
          console.warn(`Failed to fetch robots.txt for ${origin}:`, err);
          // On fetch error, allow crawling essentially (or could be strict and disallow)
          // Defaulting to Allow if robots.txt is unreachable is common, though polite crawlers might back off.
          // We'll create a dummy parser that allows everything.
          parser = robotsParser(robotsUrl, '');
          this.setCachedParser(origin, parser);
        }
      }

      return parser.isAllowed(url, userAgent) ?? true;
    } catch (e) {
      console.error('Error checking robots.txt:', e);
      return true; // Default allow on url parse error
    }
  }

  private getCachedParser(origin: string): any | null {
    const item = this.cache.get(origin);
    if (!item) return null;

    if (Date.now() > item.expiresAt) {
      this.cache.delete(origin);
      return null;
    }
    return item.parser;
  }

  private setCachedParser(origin: string, parser: any) {
    // Evict if full
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) this.cache.delete(firstKey);
    }

    this.cache.set(origin, {
      parser,
      expiresAt: Date.now() + this.TTL_MS,
    });
  }
}
