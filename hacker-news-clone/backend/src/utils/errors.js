/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, status = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.status = status;
    this.code = code;
    this.name = 'APIError';
  }
}

/**
 * Error codes enum
 */
const ErrorCodes = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  DUPLICATE_ENTRY: 'DUPLICATE_ENTRY',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  ACCOUNT_LOCKED: 'ACCOUNT_LOCKED',
  EMAIL_NOT_VERIFIED: 'EMAIL_NOT_VERIFIED',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  BAD_REQUEST: 'BAD_REQUEST',
};

/**
 * Create validation error
 */
function validationError(message) {
  return new APIError(message, 400, ErrorCodes.VALIDATION_ERROR);
}

/**
 * Create unauthorized error
 */
function unauthorizedError(message = 'Unauthorized') {
  return new APIError(message, 401, ErrorCodes.UNAUTHORIZED);
}

/**
 * Create forbidden error
 */
function forbiddenError(message = 'Forbidden') {
  return new APIError(message, 403, ErrorCodes.FORBIDDEN);
}

/**
 * Create not found error
 */
function notFoundError(message = 'Resource not found') {
  return new APIError(message, 404, ErrorCodes.NOT_FOUND);
}

/**
 * Create duplicate entry error
 */
function duplicateError(message = 'Duplicate entry') {
  return new APIError(message, 409, ErrorCodes.DUPLICATE_ENTRY);
}

/**
 * Create rate limit error
 */
function rateLimitError(message = 'Rate limit exceeded') {
  return new APIError(message, 429, ErrorCodes.RATE_LIMIT_EXCEEDED);
}

/**
 * Create account locked error
 */
function accountLockedError(message = 'Account is locked') {
  return new APIError(message, 423, ErrorCodes.ACCOUNT_LOCKED);
}

/**
 * Global error handler middleware
 */
function errorHandler(err, req, res, next) {
  // Log error
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
  });

  // Handle APIError
  if (err instanceof APIError) {
    return res.status(err.status).json({
      error: {
        code: err.code,
        message: err.message,
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
      },
    });
  }

  // Handle validation errors
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: {
        code: ErrorCodes.VALIDATION_ERROR,
        message: err.message,
      },
    });
  }

  // Handle JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: {
        code: ErrorCodes.UNAUTHORIZED,
        message: 'Invalid token',
      },
    });
  }

  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      error: {
        code: ErrorCodes.UNAUTHORIZED,
        message: 'Token expired',
      },
    });
  }

  // Default error response
  res.status(500).json({
    error: {
      code: ErrorCodes.INTERNAL_ERROR,
      message: 'An unexpected error occurred',
      ...(process.env.NODE_ENV === 'development' && {
        originalMessage: err.message,
        stack: err.stack
      }),
    },
  });
}

/**
 * Async handler wrapper to catch errors
 */
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

module.exports = {
  APIError,
  ErrorCodes,
  validationError,
  unauthorizedError,
  forbiddenError,
  notFoundError,
  duplicateError,
  rateLimitError,
  accountLockedError,
  errorHandler,
  asyncHandler,
};
