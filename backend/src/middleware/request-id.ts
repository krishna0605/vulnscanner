import { FastifyInstance } from 'fastify';
import crypto from 'crypto';

export const registerRequestId = (fastify: FastifyInstance) => {
  fastify.addHook('onRequest', (request, reply, done) => {
    // Use existing X-Request-ID if present (for tracing across services), or generate new one
    request.id = (request.headers['x-request-id'] as string) || crypto.randomUUID();

    // Add request ID to response headers
    reply.header('x-request-id', request.id);

    done();
  });
};
