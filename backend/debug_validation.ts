import { z } from 'zod';

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

const payload = {
  projectId: 'c0eebc99-sc0b-4ef8-bb6d-6bb8bd380a13', // Assuming this is valid UUID format, if not I'll fix
  targetUrl: 'https://indrashiluniversity.edu.in/',
  config: {
    scanType: 'deep',
    maxDepth: 3,
    maxPages: 200,
    checkHeaders: true,
    checkMixedContent: true,
    checkComments: true, // Note: checkComments is in Payload but NOT in Schema??
    isScheduled: false,
    scheduleCron: null,
    authEnabled: true,
    authLoginUrl: '',
    authUsername: '',
    authPassword: '',
    vectorSQLi: true,
    vectorXSS: true,
    vectorSSRF: true,
    vectorMisconfig: true,
    rateLimit: 100,
    concurrency: 20,
  },
};

// Check 'checkComments'
// Schema above doesn't have checkComments!
// Form output HAS checkComments.

try {
  startScanSchema.parse(payload);
  console.log('Validation Passed');
} catch (e) {
  console.error('Validation Failed:', JSON.stringify(e.errors, null, 2));
}
