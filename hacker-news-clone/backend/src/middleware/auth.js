const jwt = require('jsonwebtoken');
const { unauthorizedError, forbiddenError } = require('../utils/errors');
const { query } = require('../config/database');

/**
 * Generate JWT token
 */
function generateToken(user) {
  const payload = {
    id: user.id,
    username: user.username,
    email: user.email,
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRY || '24h',
  });
}

/**
 * Generate refresh token
 */
function generateRefreshToken(user) {
  const payload = {
    id: user.id,
    type: 'refresh',
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_REFRESH_EXPIRY || '7d',
  });
}

/**
 * Verify JWT token
 */
function verifyToken(token) {
  try {
    return jwt.verify(token, process.env.JWT_SECRET);
  } catch (error) {
    throw unauthorizedError('Invalid or expired token');
  }
}

/**
 * Authentication middleware
 * Verifies JWT token and attaches user to request
 */
async function authenticate(req, res, next) {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw unauthorizedError('No token provided');
    }

    const token = authHeader.substring(7);

    // Verify token
    const decoded = verifyToken(token);

    // Get user from database
    const result = await query(
      'SELECT id, username, email, karma, is_moderator, is_shadowbanned FROM users WHERE id = $1',
      [decoded.id]
    );

    if (result.rows.length === 0) {
      throw unauthorizedError('User not found');
    }

    const user = result.rows[0];

    // Check if user is shadowbanned
    if (user.is_shadowbanned) {
      throw forbiddenError('Account is restricted');
    }

    // Attach user to request
    req.user = user;

    next();
  } catch (error) {
    next(error);
  }
}

/**
 * Optional authentication middleware
 * Attaches user if token is valid, but doesn't fail if no token
 */
async function optionalAuth(req, res, next) {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return next();
    }

    const token = authHeader.substring(7);
    const decoded = verifyToken(token);

    const result = await query(
      'SELECT id, username, email, karma, is_moderator, is_shadowbanned FROM users WHERE id = $1',
      [decoded.id]
    );

    if (result.rows.length > 0) {
      req.user = result.rows[0];
    }

    next();
  } catch (error) {
    // Ignore auth errors for optional auth
    next();
  }
}

/**
 * Moderator-only middleware
 */
function requireModerator(req, res, next) {
  if (!req.user) {
    return next(unauthorizedError('Authentication required'));
  }

  if (!req.user.is_moderator) {
    return next(forbiddenError('Moderator access required'));
  }

  next();
}

/**
 * Check if user can edit content
 * Only original author or moderator can edit
 */
function canEdit(userId, contentUserId, isModerator = false) {
  return userId === contentUserId || isModerator;
}

/**
 * Check if user can delete content
 * Only original author or moderator can delete
 */
function canDelete(userId, contentUserId, isModerator = false) {
  return userId === contentUserId || isModerator;
}

/**
 * Check if user can vote
 * Users need 50 karma to vote on comments
 */
function canVoteOnComments(karma) {
  return karma >= 50;
}

module.exports = {
  generateToken,
  generateRefreshToken,
  verifyToken,
  authenticate,
  optionalAuth,
  requireModerator,
  canEdit,
  canDelete,
  canVoteOnComments,
};
