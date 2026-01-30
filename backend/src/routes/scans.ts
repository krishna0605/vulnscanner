import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { supabase } from '../lib/supabase';
import { DatabaseError, NotFoundError } from '../lib/errors';
import { success } from '../lib/response';
import { validateParams, idParamSchema } from '../lib/validators';

const startScanSchema = z.object({
  projectId: z.string().uuid(),
  targetUrl: z.string().url(),
  config: z
    .object({
      scanType: z.enum(['quick', 'standard', 'deep']).optional(),
      maxDepth: z.number().optional(),
      maxPages: z.number().optional(),
      checkHeaders: z.boolean().optional(),
      checkMixedContent: z.boolean().optional(),
      checkRobots: z.boolean().optional(),
      checkComments: z.boolean().optional(),
      userAgent: z.string().optional(),
      // Scheduling
      isScheduled: z.boolean().optional(),
      scheduleCron: z.string().nullable().optional(),
      // Auth
      authEnabled: z.boolean().optional(),
      authLoginUrl: z.string().optional(),
      authUsername: z.string().optional(),
      authPassword: z.string().optional(),
      // Vectors
      vectorSQLi: z.boolean().optional(),
      vectorXSS: z.boolean().optional(),
      vectorSSRF: z.boolean().optional(),
      vectorMisconfig: z.boolean().optional(),
      // Performance
      rateLimit: z.number().optional(),
      concurrency: z.number().optional(),
    })
    .optional(),
});

export async function scanRoutes(fastify: FastifyInstance) {
  fastify.post(
    '/scans',
    {
      schema: {
        description: 'Start a new vulnerability scan',
        tags: ['Scans'],
        summary: 'Create a new scan',
        security: [{ bearerAuth: [] }],
        body: {
          type: 'object',
          required: ['projectId', 'targetUrl'],
          properties: {
            projectId: { type: 'string', format: 'uuid' },
            targetUrl: { type: 'string', format: 'uri' },
            config: {
              type: 'object',
              properties: {
                scanType: { type: 'string', enum: ['quick', 'standard', 'deep'] },
                maxDepth: { type: 'number' },
                authEnabled: { type: 'boolean' },
              },
            },
          },
        },
        response: {
          200: {
            description: 'Scan created successfully',
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: {
                type: 'object',
                properties: {
                  id: { type: 'string', format: 'uuid' },
                  status: { type: 'string' },
                  target_url: { type: 'string' },
                },
              },
            },
          },
        },
      },
    },
    async (request, reply) => {
      // 1. Parse Input (Global handler catches ZodError)
      const bodyString = JSON.stringify(request.body);
      const { projectId, targetUrl, config } = startScanSchema.parse(JSON.parse(bodyString));

      request.log.info({ projectId, targetUrl }, `[API] Creating scan for ${targetUrl}`);

      // 2. Create Scan record
      const { data: scan, error } = await supabase
        .from('scans')
        .insert({
          project_id: projectId,
          target_url: targetUrl,
          status: 'queued',
          config: config || {},
          type: (config as any)?.scanType || 'quick',
        })
        .select()
        .single();

      if (error) {
        throw new DatabaseError(error.message);
      }

      // 3. Trigger Crawler
      // In production, this would be a real job queue.
      request.log.info({ scanId: scan.id, targetUrl }, `[Scanner] Triggering scan`);

      try {
        const { CrawlerService } = await import('../lib/crawler');
        const crawler = new CrawlerService();

        // Fire and forget
        crawler.scan(scan.id, projectId, targetUrl, config).catch((err) => {
          request.log.error({ err, scanId: scan.id }, `[Scanner] Background Error`);
        });
      } catch (crawlerError: any) {
        request.log.error({ err: crawlerError }, '[API] Crawler Init Failed');
        await supabase.from('scans').update({ status: 'failed' }).eq('id', scan.id);
        throw new DatabaseError(`Failed to initialize crawler: ${crawlerError.message}`);
      }

      return success(scan);
    }
  );

  fastify.get(
    '/scans/:id',
    {
      schema: {
        description: 'Get scan details by ID',
        tags: ['Scans'],
        summary: 'Get scan details',
        params: {
          type: 'object',
          properties: {
            id: { type: 'string', format: 'uuid', description: 'Scan ID' },
          },
        },
        response: {
          200: {
            description: 'Scan details',
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  status: { type: 'string' },
                  findings: { type: 'array', items: { type: 'object' } },
                },
              },
            },
          },
        },
      },
    },
    async (request, reply) => {
      // Validate UUID format
      const { id } = validateParams(idParamSchema, request.params);

      const { data, error } = await supabase
        .from('scans')
        .select('*, findings(*), assets(count)')
        .eq('id', id)
        .single();

      if (error || !data) {
        throw new NotFoundError('Scan not found');
      }

      return success(data);
    }
  );
}
