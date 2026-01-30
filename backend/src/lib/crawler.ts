import { chromium, Browser, Page } from 'playwright';
import { supabase } from './supabase';
import { URL } from 'url';
import { URLNormalizer } from './normalizer';
import { TechnologyFingerprinter, Technology } from './fingerprinter';
import { RobotsService } from './robots';
import { logger } from './logger';

export interface ScanConfig {
  scanType?: 'quick' | 'standard' | 'deep';
  maxDepth?: number;
  maxPages?: number;
  checkHeaders?: boolean;
  checkMixedContent?: boolean;
  checkComments?: boolean;
  userAgent?: string;
  checkRobots?: boolean;

  // Advanced
  isScheduled?: boolean; // Not used by crawler directly but passed
  authEnabled?: boolean;
  authLoginUrl?: string;
  authUsername?: string;
  authPassword?: string;

  vectorSQLi?: boolean;
  vectorXSS?: boolean;
  vectorSSRF?: boolean;
  vectorMisconfig?: boolean;

  rateLimit?: number;
  concurrency?: number;
}

interface ScanQueueItem {
  url: string;
  depth: number;
}

export class CrawlerService {
  private visited = new Set<string>();
  private queue: ScanQueueItem[] = [];
  private scanId: string = '';
  private projectId: string = '';
  private config: ScanConfig = {};
  private pagesScanned = 0;

  // New Modules
  private normalizer: URLNormalizer;
  private fingerprinter: TechnologyFingerprinter;
  private robotsService: RobotsService;

  // Blocked IP patterns for SSRF protection
  private static readonly BLOCKED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '::1', '[::1]'];

  private static readonly BLOCKED_IP_PATTERNS = [
    /^10\./, // 10.0.0.0/8 (Class A private)
    /^172\.(1[6-9]|2[0-9]|3[01])\./, // 172.16.0.0/12 (Class B private)
    /^192\.168\./, // 192.168.0.0/16 (Class C private)
    /^169\.254\./, // Link-local
    /^127\./, // Loopback
    /^0\./, // Current network
  ];

  constructor() {
    this.normalizer = new URLNormalizer();
    this.fingerprinter = new TechnologyFingerprinter();
    this.robotsService = new RobotsService();
  }

  /**
   * Validates URL to prevent SSRF attacks
   * Blocks internal IPs, localhost, and private network ranges
   */
  private isUrlSafe(urlString: string): { safe: boolean; reason?: string } {
    try {
      const parsed = new URL(urlString);
      const hostname = parsed.hostname.toLowerCase();

      // Block localhost and common internal hostnames
      if (CrawlerService.BLOCKED_HOSTS.includes(hostname)) {
        return { safe: false, reason: `Blocked host: ${hostname}` };
      }

      // Block internal TLDs
      if (
        hostname.endsWith('.local') ||
        hostname.endsWith('.internal') ||
        hostname.endsWith('.localhost')
      ) {
        return { safe: false, reason: `Blocked internal TLD: ${hostname}` };
      }

      // Block private IP ranges
      for (const pattern of CrawlerService.BLOCKED_IP_PATTERNS) {
        if (pattern.test(hostname)) {
          return { safe: false, reason: `Blocked private IP: ${hostname}` };
        }
      }

      // Block non-http(s) protocols
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return { safe: false, reason: `Blocked protocol: ${parsed.protocol}` };
      }

      return { safe: true };
    } catch (e) {
      return { safe: false, reason: 'Invalid URL format' };
    }
  }

  private async log(message: string, level: 'info' | 'warn' | 'error' | 'success' = 'info') {
    // Map 'success' to 'info' for pino, but start with emoji or specific msg
    const pinoLevel = level === 'success' ? 'info' : level;
    logger[pinoLevel]({ scanId: this.scanId }, `[Scanner] ${message}`);

    await supabase.from('scan_logs').insert({
      scan_id: this.scanId,
      message,
      level,
      timestamp: new Date().toISOString(),
    });
  }

  private async updateProgress(progress: number, action: string) {
    try {
      await supabase
        .from('scans')
        .update({
          progress,
          current_action: action,
        })
        .eq('id', this.scanId);
    } catch (e) {
      console.error('Failed to update progress', e);
    }
  }

  async scan(scanId: string, projectId: string, startUrl: string, config: ScanConfig = {}) {
    this.scanId = scanId;
    this.projectId = projectId;
    this.config = config;
    this.visited.clear();

    // SSRF Protection: Validate URL before scanning
    const urlSafetyCheck = this.isUrlSafe(startUrl);
    if (!urlSafetyCheck.safe) {
      await this.log(`🛡️ SSRF Protection: Scan rejected - ${urlSafetyCheck.reason}`, 'error');
      await supabase
        .from('scans')
        .update({
          status: 'failed',
          current_action: `Security: ${urlSafetyCheck.reason}`,
        })
        .eq('id', scanId);
      return;
    }

    // Normalize start URL
    const normalizedStart = this.normalizer.normalizeUrl(startUrl);
    this.queue = [{ url: normalizedStart, depth: 0 }];
    this.pagesScanned = 0;

    // Defaults
    const maxDepth = config.maxDepth ?? (config.scanType === 'quick' ? 0 : 2);
    const maxPages = config.maxPages ?? (config.scanType === 'deep' ? 200 : 50);
    const userAgent = config.userAgent || 'VulnScanner-Bot/1.0';

    await this.log(
      `Initializing scan for ${startUrl} with config: ${JSON.stringify(config)}`,
      'info'
    );
    await this.updateProgress(5, 'Launching engine...');

    let browser: Browser | null = null;

    try {
      browser = await chromium.launch();
      const context = await browser.newContext({
        ignoreHTTPSErrors: true,
        userAgent: userAgent,
      });

      // 1. Authentication Check
      if (this.config.authEnabled && this.config.authLoginUrl) {
        await this.log(`Attempting authentication at ${this.config.authLoginUrl}`, 'info');
        const authPage = await context.newPage();
        try {
          await this.authenticate(authPage);
          await this.log('Authentication successful (session cookies established)', 'success');
        } catch (e: any) {
          await this.log(`Authentication failed: ${e.message}`, 'error');
          // Proceed anyway? Or stop? User might want to scan what's public if auth fails.
          // For now, log error and proceed.
        } finally {
          await authPage.close();
        }
      }

      // Concurrency Control
      const concurrency = this.config.concurrency || 1;
      const rateLimitDelay = this.config.rateLimit ? Math.floor(1000 / this.config.rateLimit) : 0;

      // We need a proper queue processor for concurrency
      // For MVP with concurrency > 1, we can't use simple while loop easily without managing promises.
      // Let's use a "worker" model.

      const activePromises = new Set<Promise<void>>();

      while (this.queue.length > 0 || activePromises.size > 0) {
        // Enforce max pages limit global check
        if (this.pagesScanned >= maxPages) break;

        // Fill the pool
        while (
          this.queue.length > 0 &&
          activePromises.size < concurrency &&
          this.pagesScanned < maxPages
        ) {
          const { url, depth } = this.queue.shift()!;

          if (this.visited.has(url)) continue;

          // Robots Check
          if (this.config.checkRobots !== false) {
            // Optimization: Cache robots.txt or check once per domain
            const allowed = await this.robotsService.isAllowed(url, userAgent);
            if (!allowed) {
              // Log skip
              continue;
            }
          }

          this.visited.add(url);
          this.pagesScanned++;

          // Create a promise for this page
          const p = (async () => {
            const page = await context.newPage();
            try {
              await this.updateProgress(
                Math.min(90, Math.floor((this.pagesScanned / maxPages) * 100)),
                `Scanning: ${url}`
              );
              await this.processPage(page, url, depth, maxDepth);
            } catch (e: any) {
              console.error(`Error scanning ${url}`, e);
            } finally {
              await page.close();
              if (rateLimitDelay > 0) await new Promise((r) => setTimeout(r, rateLimitDelay));
            }
          })();

          activePromises.add(p);
          p.finally(() => activePromises.delete(p));
        }

        // Wait for at least one to finish before looping again to refill
        if (activePromises.size > 0) {
          await Promise.race(activePromises);
        } else if (this.queue.length === 0) {
          break; // Done
        }
      }

      await this.log(`Scan complete. Analyzed ${this.pagesScanned} pages.`, 'success');
      await this.updateProgress(100, 'Completed');
      await supabase
        .from('scans')
        .update({
          status: 'completed',
          current_action: 'Completed',
          completed_at: new Date().toISOString(),
        })
        .eq('id', scanId);
    } catch (error: any) {
      logger.error({ err: error, scanId: scanId }, `[Crawler] Fatal Error`);
      await this.log(`Critical Engine Error: ${error.message}`, 'error');
      await supabase
        .from('scans')
        .update({ status: 'failed', current_action: 'Failed' })
        .eq('id', scanId);
    } finally {
      if (browser) await browser.close();
    }
  }

  public async authenticate(page: Page) {
    if (!this.config.authLoginUrl || !this.config.authUsername || !this.config.authPassword) {
      throw new Error('Missing auth credentials');
    }

    await page.goto(this.config.authLoginUrl, { waitUntil: 'networkidle' });

    const selectors = {
      user: [
        'input[name="user"]',
        'input[name="username"]',
        'input[type="email"]',
        '#username',
        '#email',
      ],
      pass: ['input[name="password"]', 'input[type="password"]', '#password'],
      submit: [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Login")',
        'button:has-text("Sign In")',
      ],
    };

    let userFound = false;
    for (const sel of selectors.user) {
      if (await page.$(sel)) {
        await page.type(sel, this.config.authUsername);
        userFound = true;
        break;
      }
    }

    let passFound = false;
    for (const sel of selectors.pass) {
      if (await page.$(sel)) {
        await page.type(sel, this.config.authPassword);
        passFound = true;
        break;
      }
    }

    if (userFound && passFound) {
      for (const sel of selectors.submit) {
        if (await page.$(sel)) {
          await Promise.all([
            page.waitForNavigation({ timeout: 10000 }).catch(() => {}),
            page.click(sel),
          ]);
          return;
        }
      }
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2000);
    } else {
      throw new Error('Could not identify login fields automatically.');
    }
  }

  private async processPage(page: Page, url: string, depth: number, maxDepth: number) {
    await this.log(`Navigating to ${url}`, 'info');

    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
    if (!response) {
      await this.log(`No response for ${url}`, 'warn');
      return;
    }

    const status = response.status();
    const headers = response.headers();
    const content = await page.content();

    // Insert Asset (Page Inventory)
    try {
      const pageTitle = (await page.title()) || '';
      await supabase.from('assets').insert({
        project_id: this.projectId,
        scan_id: this.scanId,
        url: url,
        type: 'page',
        status_code: status,
        title: pageTitle,
        metadata: {
          headers: headers,
        },
      });
    } catch (assetError) {
      // Non-critical, just log
      // console.error('[Scanner] Failed to save asset', assetError);
    }

    // 0. Fingerprint Technology
    try {
      const fingerprint = this.fingerprinter.analyze(headers, content);

      if (fingerprint.technologies.length > 0) {
        const techNames = fingerprint.technologies.map((t) => t.name).join(', ');
        // Only log distinct stacks once per domain ideally, but here per page is okay for MVP
        if (depth === 0) {
          await this.log(`Detected Technologies: ${techNames}`, 'success');
        }

        // Update status of asset with technologies
        // Note: Ideally we would do this in the initial insert, but fingerprint is calculated after content is read.
        // Actually, we can just update the metadata of the asset we just created.
        // Or better, move the asset insertion AFTER fingerprinting to include techs in metadata.
        await supabase
          .from('assets')
          .update({
            metadata: {
              headers: headers,
              technologies: fingerprint.technologies,
            },
          })
          .match({ scan_id: this.scanId, url: url });
      }

      // Report Security Header Issues from Fingerprinter
      if (fingerprint.securityScore < 70) {
        await this.reportFinding({
          title: 'Weak Security Configuration',
          description: `Security Header Score is low (${fingerprint.securityScore}/100). Missing critical headers.`,
          severity: 'low',
          location: url,
          evidence: `Present Headers: ${Object.keys(fingerprint.securityHeaders).join(', ')}`,
          cwe_id: 'CWE-693',
        });
      }
    } catch (e) {
      console.error('Fingerprinting failed', e);
    }

    // 1. Analyze Headers (Legacy + specific checks)
    if (this.config.checkHeaders !== false) {
      if (!headers['content-security-policy']) {
        await this.reportFinding({
          title: 'Missing Content-Security-Policy',
          description: 'CSP header is missing, increasing XSS risk.',
          severity: 'medium',
          location: url,
          evidence: `Headers: ${JSON.stringify(headers)}`,
          cwe_id: 'CWE-1021',
        });
      }
      if (!headers['x-frame-options']) {
        await this.reportFinding({
          title: 'Missing X-Frame-Options',
          description: 'Site potentially vulnerable to Clickjacking.',
          severity: 'low',
          location: url,
          evidence: 'Header missing',
          cwe_id: 'CWE-1021',
        });
      }
    }

    // 2. Analyze Content (Mixed Content, Comments)
    if (
      this.config.checkMixedContent !== false &&
      url.startsWith('https://') &&
      content.includes('http://')
    ) {
      await this.reportFinding({
        title: 'Mixed Content Detected',
        description: 'HTTPS page loads HTTP resources.',
        severity: 'high',
        location: url,
        evidence: 'Found http:// link in source',
        cwe_id: 'CWE-311',
      });
    }

    if (this.config.checkComments !== false && content.includes('<!--')) {
      const matches = content.match(/<!--(.*?)-->/g);
      const sensitive = matches?.filter((m) => /TODO|FIXME|password|secret|key/i.test(m));
      if (sensitive && sensitive.length > 0) {
        await this.reportFinding({
          title: 'Sensitive Comments Found',
          description: `Found ${sensitive.length} suspicious HTML comments.`,
          severity: 'low',
          location: url,
          evidence: sensitive.slice(0, 5).join('\n'),
          cwe_id: 'CWE-615',
        });
      }
    }

    // 3. Asset Discovery (Links)
    // Only crawl deeper if we haven't hit max depth and it's same origin
    if (depth < maxDepth) {
      const hrefs = await page.$$eval('a', (as) => as.map((a) => a.href));

      let newLinksCount = 0;
      for (const href of hrefs) {
        // Enhanced normalization logic
        const normalized = this.normalizer.normalizeUrl(href);

        if (
          normalized &&
          this.normalizer.isValidUrl(normalized) &&
          this.normalizer.isSameDomain(normalized, url) &&
          !this.visited.has(normalized)
        ) {
          // Future: Check robots.txt here too to avoid queueing disallowed links?
          // For now, checking at queue processing is safer/easier.
          this.queue.push({ url: normalized, depth: depth + 1 });
          newLinksCount++;
        }
      }
      if (newLinksCount > 0) {
        await this.log(`Found ${newLinksCount} new links to crawl on ${url}`, 'info');
      }
    }
  }

  private async reportFinding(finding: {
    title: string;
    description: string;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
    location: string;
    evidence?: string;
    remediation?: string;
    cwe_id?: string;
  }) {
    await supabase.from('findings').insert({
      scan_id: this.scanId,
      ...finding,
    });
    await this.log(
      `Finding: ${finding.title} (${finding.severity})`,
      finding.severity === 'info' ? 'info' : 'warn'
    );
  }
}
