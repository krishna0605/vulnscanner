import { env } from './env';

type LogLevel = 'info' | 'warn' | 'error' | 'success';

class ConvexScannerClient {
  private siteUrl = env.CONVEX_SITE_URL?.replace(/\/$/, '');
  private token = env.SCANNER_SERVICE_TOKEN;

  private async post<T = any>(path: string, body: unknown): Promise<T | null> {
    if (!this.siteUrl || !this.token) {
      throw new Error('Convex scanner integration is not configured');
    }

    const response = await fetch(`${this.siteUrl}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok || data?.success === false) {
      throw new Error(data?.error || `Convex request failed: ${response.status}`);
    }
    return data?.data ?? data;
  }

  async markStarted(scanId: string, node?: string) {
    await this.post('/scanner/started', { scanId, node });
  }

  async addLog(scanId: string, message: string, level: LogLevel) {
    await this.post('/scanner/log', {
      scanId,
      message,
      level,
      timestamp: Date.now(),
    });
  }

  async updateProgress(scanId: string, progress: number, currentAction: string) {
    await this.post('/scanner/progress', { scanId, progress, currentAction });
  }

  async addAsset(asset: {
    projectId: string;
    scanId?: string;
    url: string;
    type: string;
    statusCode?: number;
    title?: string;
    metadata?: unknown;
    riskScore?: number;
  }) {
    await this.post('/scanner/asset', asset);
  }

  async addFinding(finding: {
    scanId: string;
    projectId: string;
    title: string;
    description?: string;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
    location?: string;
    evidence?: string;
    remediation?: string;
    cweId?: string;
    cveId?: string;
    cvssScore?: number;
  }) {
    await this.post('/scanner/finding', finding);
  }

  async completeScan(scanId: string, score?: number) {
    await this.post('/scanner/complete', { scanId, score });
  }

  async failScan(scanId: string, message: string) {
    await this.post('/scanner/fail', { scanId, message });
  }

  async getScanStatus(scanId: string): Promise<string | null> {
    const data = await this.post<{ status?: string } | null>('/scanner/status', { scanId });
    return data?.status ?? null;
  }
}

export const convexScanner = new ConvexScannerClient();
