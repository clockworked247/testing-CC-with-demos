const rateLimit = require('express-rate-limit');
const { rateLimitError } = require('../utils/errors');

/**
 * General API rate limiter
 */
const apiLimiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: 'Too many requests from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    throw rateLimitError('Too many requests, please try again later');
  },
});

/**
 * Story submission rate limiter
 * 5 stories per hour per user
 */
const storySubmitLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  message: 'Too many story submissions, please try again later',
  keyGenerator: (req) => {
    return req.user ? req.user.id.toString() : req.ip;
  },
  handler: (req, res) => {
    throw rateLimitError('Story submission limit exceeded (5 per hour)');
  },
});

/**
 * Comment rate limiter
 * 30 comments per hour per user
 */
const commentLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 30,
  message: 'Too many comments, please try again later',
  keyGenerator: (req) => {
    return req.user ? req.user.id.toString() : req.ip;
  },
  handler: (req, res) => {
    throw rateLimitError('Comment limit exceeded (30 per hour)');
  },
});

/**
 * Vote rate limiter
 * 100 votes per hour per user
 */
const voteLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 100,
  message: 'Too many votes, please try again later',
  keyGenerator: (req) => {
    return req.user ? req.user.id.toString() : req.ip;
  },
  handler: (req, res) => {
    throw rateLimitError('Vote limit exceeded (100 per hour)');
  },
});

/**
 * Auth rate limiter (login/register)
 * Stricter limits for authentication endpoints
 */
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,
  message: 'Too many authentication attempts, please try again later',
  skipSuccessfulRequests: true,
  handler: (req, res) => {
    throw rateLimitError('Too many authentication attempts, please try again later');
  },
});

module.exports = {
  apiLimiter,
  storySubmitLimiter,
  commentLimiter,
  voteLimiter,
  authLimiter,
};
