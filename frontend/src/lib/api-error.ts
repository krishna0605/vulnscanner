export class APIError extends Error {
  public code: string;
  public details?: any;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', details?: any) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.details = details;
  }
}

export function parseAPIError(error: any): APIError {
  if (error instanceof APIError) {
    return error;
  }

  // Handle standard backend error format
  // Format: { success: false, error: { code, message, details } }
  if (error.response?.data?.error) {
    const { message, code, details } = error.response.data.error;
    return new APIError(message, code, details);
  }

  // Handle generic axios errors
  if (error.response) {
    return new APIError(
      error.response.statusText || 'Request failed',
      `HTTP_${error.response.status}`
    );
  }

  // Handle network errors
  if (error.request) {
    return new APIError('Network error. Please check your connection.', 'NETWORK_ERROR');
  }

  return new APIError(error.message || 'An unexpected error occurred');
}
