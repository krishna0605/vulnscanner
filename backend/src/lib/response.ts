/**
 * Standardized API Response Interfaces
 * Ensures consistent response structure across the entire API
 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}

/**
 * Creates a success response
 */
export function success<T>(data: T, meta?: ApiResponse['meta']): ApiResponse<T> {
  return {
    success: true,
    data,
    meta,
  };
}

/**
 * Creates an error response
 */
export function error(code: string, message: string, details?: unknown): ApiResponse<null> {
  return {
    success: false,
    error: {
      code,
      message,
      details,
    },
  };
}

/**
 * Common OpenAPI Response schemas
 */
export const responseSchemas = {
  success: {
    type: 'object',
    properties: {
      success: { type: 'boolean', const: true },
      data: { type: 'object' },
    },
  },
  error: {
    type: 'object',
    properties: {
      success: { type: 'boolean', const: false },
      error: {
        type: 'object',
        properties: {
          code: { type: 'string' },
          message: { type: 'string' },
        },
      },
    },
  },
};
