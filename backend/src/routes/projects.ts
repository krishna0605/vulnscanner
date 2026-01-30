import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { supabase } from '../lib/supabase';
import { DatabaseError, ValidationError } from '../lib/errors';
import { success } from '../lib/response';

export async function projectRoutes(fastify: FastifyInstance) {
  fastify.post(
    '/projects',
    {
      schema: {
        description: 'Create a new project',
        tags: ['Projects'],
        security: [{ bearerAuth: [] }],
        body: {
          type: 'object',
          required: ['name'],
          properties: {
            name: { type: 'string' },
            description: { type: 'string' },
          },
        },
        response: {
          200: {
            description: 'Project created',
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: {
                type: 'object',
                properties: {
                  id: { type: 'string', format: 'uuid' },
                  name: { type: 'string' },
                },
              },
            },
          },
        },
      },
    },
    async (request, reply) => {
      // Global handler catches ZodError
      const createProjectSchema = z.object({
        name: z.string().min(1),
        description: z.string().optional(),
      });

      // Validate body (userId coming from token)
      const { name, description } = createProjectSchema.parse(request.body);
      const userId = (request as any).user?.id;

      if (!userId) {
        throw new ValidationError('User not authenticated');
      }

      const { data, error } = await supabase
        .from('projects')
        .insert({ name, description, user_id: userId })
        .select()
        .single();

      if (error) {
        throw new DatabaseError(error.message);
      }

      return success(data);
    }
  );

  fastify.get(
    '/projects',
    {
      schema: {
        description: 'List user projects',
        tags: ['Projects'],
        security: [{ bearerAuth: [] }],
        response: {
          200: {
            description: 'List of projects',
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    id: { type: 'string' },
                    name: { type: 'string' },
                  },
                },
              },
            },
          },
        },
      },
    },
    async (request, reply) => {
      const userId = (request as any).user?.id;

      if (!userId) {
        throw new ValidationError('User not authenticated');
      }

      const { data, error } = await supabase.from('projects').select('*').eq('user_id', userId);

      if (error) {
        throw new DatabaseError(error.message);
      }

      return success(data);
    }
  );
}
