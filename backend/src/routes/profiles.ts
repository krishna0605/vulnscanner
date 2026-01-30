import { FastifyInstance } from 'fastify';
import { supabase } from '../lib/supabase';
import { z } from 'zod';
import { DatabaseError } from '../lib/errors';
import { success } from '../lib/response';
import { validateParams, idParamSchema } from '../lib/validators';

const createProfileSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
  config: z.record(z.any()), // Flexible config object
});

export async function profileRoutes(fastify: FastifyInstance) {
  // GET /profiles - List all profiles
  fastify.get(
    '/profiles',
    {
      schema: {
        description: 'List scan profiles',
        tags: ['Profiles'],
        response: {
          200: {
            description: 'List of profiles',
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: { type: 'array', items: { type: 'object' } },
            },
          },
        },
      },
    },
    async (request, reply) => {
      const { data, error } = await supabase.from('scan_profiles').select('*').order('name');

      if (error) throw new DatabaseError(error.message);
      return success(data);
    }
  );

  // POST /profiles - Create new profile
  fastify.post(
    '/profiles',
    {
      schema: {
        description: 'Create a new scan profile',
        tags: ['Profiles'],
        body: {
          type: 'object',
          required: ['name'],
          properties: {
            name: { type: 'string' },
            description: { type: 'string' },
            config: { type: 'object' },
          },
        },
        response: {
          200: {
            description: 'Profile created',
            type: 'object',
            properties: {
              success: { type: 'boolean', const: true },
              data: { type: 'object' },
            },
          },
        },
      },
    },
    async (request, reply) => {
      const body = createProfileSchema.parse(request.body);

      const { data, error } = await supabase
        .from('scan_profiles')
        .insert({
          name: body.name,
          description: body.description,
          config: body.config,
        })
        .select()
        .single();

      if (error) throw new DatabaseError(error.message);
      return success(data);
    }
  );

  // DELETE /profiles/:id - Delete profile
  fastify.delete('/profiles/:id', async (request, reply) => {
    const { id } = validateParams(idParamSchema, request.params);

    const { error } = await supabase.from('scan_profiles').delete().eq('id', id);

    if (error) throw new DatabaseError(error.message);
    return success({ deleted: true });
  });
}
