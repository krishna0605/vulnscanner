import { z } from 'zod';

// UUID validation schema
export const uuidSchema = z.string().uuid('Invalid UUID format');

// Common param schemas
export const idParamSchema = z.object({
  id: uuidSchema,
});

// Pagination schema
export const paginationSchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
});

// Helper to validate params
export function validateParams<T>(schema: z.ZodSchema<T>, params: unknown): T {
  return schema.parse(params);
}
