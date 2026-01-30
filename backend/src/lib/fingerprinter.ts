/**
 * Technology fingerprinting component.
 * Ported from legacy fingerprinter.py
 */

export interface Technology {
  name: string;
  category:
    | 'web_server'
    | 'language'
    | 'framework'
    | 'cms'
    | 'javascript'
    | 'css_framework'
    | 'analytics'
    | 'cdn'
    | 'generator'
    | 'other';
  confidence: 'high' | 'medium' | 'low';
}

interface Signature {
  headers?: string[];
  patterns?: RegExp[];
  htmlPatterns?: RegExp[];
  category: Technology['category'];
}

type TechSignatures = Record<string, Signature>;

export class TechnologyFingerprinter {
  private signatures: TechSignatures;
  private securityHeaders: string[];

  constructor() {
    this.signatures = this._loadSignatures();
    this.securityHeaders = [
      'strict-transport-security',
      'content-security-policy',
      'x-frame-options',
      'x-content-type-options',
      'x-xss-protection',
      'referrer-policy',
      'permissions-policy',
      'feature-policy',
      'expect-ct',
      'public-key-pins',
    ];
  }

  private _loadSignatures(): TechSignatures {
    return {
      // Web Servers
      apache: {
        headers: ['server'],
        patterns: [/apache/i, /httpd/i],
        category: 'web_server',
      },
      nginx: {
        headers: ['server'],
        patterns: [/nginx/i],
        category: 'web_server',
      },
      iis: {
        headers: ['server'],
        patterns: [/microsoft-iis/i, /iis/i],
        category: 'web_server',
      },
      cloudflare: {
        headers: ['server', 'cf-ray'],
        patterns: [/cloudflare/i],
        category: 'cdn',
      },

      // Languages
      php: {
        headers: ['x-powered-by', 'server'],
        patterns: [/php/i, /\.php/i],
        htmlPatterns: [/\.php\?/i, /\.php$/i],
        category: 'language',
      },
      'asp.net': {
        headers: ['x-powered-by', 'x-aspnet-version'],
        patterns: [/asp\.net/i, /aspnet/i],
        htmlPatterns: [/\.aspx/i, /__viewstate/i],
        category: 'language',
      },

      // Frameworks
      django: {
        headers: ['server'],
        patterns: [/django/i],
        htmlPatterns: [/csrfmiddlewaretoken/i],
        category: 'framework',
      },
      flask: {
        headers: ['server'],
        patterns: [/flask/i],
        category: 'framework',
      },
      rails: {
        headers: ['x-powered-by'],
        patterns: [/ruby/i, /rails/i],
        htmlPatterns: [/authenticity_token/i],
        category: 'framework',
      },
      express: {
        headers: ['x-powered-by'],
        patterns: [/express/i],
        category: 'framework',
      },

      // CMS
      wordpress: {
        htmlPatterns: [/wp-content/i, /wp-includes/i, /wordpress/i, /wp-json/i, /\/wp-admin\//i],
        category: 'cms',
      },
      drupal: {
        htmlPatterns: [/drupal/i, /\/sites\/default\//i, /drupal\.js/i],
        category: 'cms',
      },
      shopify: {
        htmlPatterns: [/shopify/i, /cdn\.shopify\.com/i, /myshopify\.com/i],
        category: 'cms',
      },

      // JS Libs
      jquery: {
        htmlPatterns: [/jquery/i, /jquery\.min\.js/i],
        category: 'javascript',
      },
      react: {
        htmlPatterns: [/react/i, /react\.js/i, /react\.min\.js/i, /data-reactroot/i],
        category: 'javascript',
      },
      vue: {
        htmlPatterns: [/vue\.js/i, /vue\.min\.js/i, /v-if/i, /v-for/i],
        category: 'javascript',
      },
      angular: {
        htmlPatterns: [/angular/i, /ng-app/i, /ng-controller/i],
        category: 'javascript',
      },
      bootstrap: {
        htmlPatterns: [/bootstrap/i, /bootstrap\.css/i, /bootstrap\.js/i, /col-/i, /container/i],
        category: 'css_framework',
      },

      // Analytics
      google_analytics: {
        htmlPatterns: [/google-analytics/i, /gtag/i, /ga\(/i],
        category: 'analytics',
      },
    };
  }

  public analyze(
    headers: Record<string, string>,
    html: string
  ): {
    technologies: Technology[];
    securityHeaders: Record<string, string>;
    securityScore: number;
  } {
    const detected: Technology[] = [];
    const normalizedHeaders: Record<string, string> = {};
    for (const [k, v] of Object.entries(headers)) {
      normalizedHeaders[k.toLowerCase()] = v;
    }

    // Check Signatures
    for (const [techName, sig] of Object.entries(this.signatures)) {
      let found = false;

      // Check Headers
      if (sig.headers) {
        for (const h of sig.headers) {
          if (normalizedHeaders[h]) {
            const val = normalizedHeaders[h];
            if (sig.patterns) {
              for (const p of sig.patterns) {
                if (p.test(val)) {
                  this._addTech(detected, techName, sig.category);
                  found = true;
                  break;
                }
              }
            } else {
              // Existence check
              this._addTech(detected, techName, sig.category);
              found = true;
            }
          }
          if (found) break;
        }
      }
      if (found) continue;

      // Check HTML
      if (sig.htmlPatterns && html) {
        for (const p of sig.htmlPatterns) {
          if (p.test(html)) {
            this._addTech(detected, techName, sig.category);
            break;
          }
        }
      }
    }

    // Security Headers Analysis
    const foundSecHeaders: Record<string, string> = {};
    for (const h of this.securityHeaders) {
      if (normalizedHeaders[h]) {
        foundSecHeaders[h] = normalizedHeaders[h];
      }
    }

    const securityScore = (Object.keys(foundSecHeaders).length / this.securityHeaders.length) * 100;

    return {
      technologies: detected,
      securityHeaders: foundSecHeaders,
      securityScore: Math.round(securityScore),
    };
  }

  private _addTech(list: Technology[], name: string, category: Technology['category']) {
    if (!list.find((t) => t.name === name)) {
      list.push({ name, category, confidence: 'medium' });
    }
  }
}
