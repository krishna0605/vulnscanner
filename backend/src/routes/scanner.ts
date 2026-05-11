import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { success } from '../lib/response';

const scannerRunSchema = z.object({
  scanId: z.string().min(1),
  projectId: z.string().min(1),
  targetUrl: z.string().url(),
  config: z.record(z.any()).optional(),
});

function assertScannerToken(authHeader?: string) {
  const expected = process.env.SCANNER_SERVICE_TOKEN;
  if (!expected || authHeader !== `Bearer ${expected}`) {
    const error = new Error('Unauthorized scanner request');
    (error as any).statusCode = 401;
    throw error;
  }
}

export async function scannerRoutes(fastify: FastifyInstance) {
  fastify.post('/scanner/run', async (request, reply) => {
    assertScannerToken(request.headers.authorization);
    const body = scannerRunSchema.parse(request.body);

    const { CrawlerService } = await import('../lib/crawler');
    const crawler = new CrawlerService();

    crawler.scan(body.scanId, body.projectId, body.targetUrl, body.config).catch((err) => {
      request.log.error({ err, scanId: body.scanId }, '[Scanner] Background error');
    });

    return success({ accepted: true, scanId: body.scanId });
  });

  fastify.post('/scanner/pause', async (request, reply) => {
    assertScannerToken(request.headers.authorization);
    return success({ accepted: true });
  });

  fastify.post('/scanner/resume', async (request, reply) => {
    assertScannerToken(request.headers.authorization);
    return success({ accepted: true });
  });

  fastify.post('/scanner/cancel', async (request, reply) => {
    assertScannerToken(request.headers.authorization);
    return success({ accepted: true });
  });
}
