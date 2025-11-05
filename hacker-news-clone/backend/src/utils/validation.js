const validator = require('validator');
const sanitizeHtml = require('sanitize-html');
const { validationError } = require('./errors');

/**
 * Validate username
 * - 2-15 alphanumeric characters
 * - Underscores allowed
 * - No special characters
 */
function validateUsername(username) {
  if (!username || typeof username !== 'string') {
    throw validationError('Username is required');
  }

  if (username.length < 2 || username.length > 15) {
    throw validationError('Username must be between 2 and 15 characters');
  }

  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    throw validationError('Username can only contain letters, numbers, and underscores');
  }

  return username.trim();
}

/**
 * Validate email
 */
function validateEmail(email) {
  if (!email || typeof email !== 'string') {
    throw validationError('Email is required');
  }

  if (!validator.isEmail(email)) {
    throw validationError('Invalid email format');
  }

  return email.toLowerCase().trim();
}

/**
 * Validate password
 * - Minimum 8 characters
 * - At least one number
 */
function validatePassword(password) {
  if (!password || typeof password !== 'string') {
    throw validationError('Password is required');
  }

  if (password.length < 8) {
    throw validationError('Password must be at least 8 characters');
  }

  if (!/\d/.test(password)) {
    throw validationError('Password must contain at least one number');
  }

  return password;
}

/**
 * Validate story title
 */
function validateTitle(title) {
  if (!title || typeof title !== 'string') {
    throw validationError('Title is required');
  }

  const trimmed = title.trim();

  if (trimmed.length === 0) {
    throw validationError('Title cannot be empty');
  }

  if (trimmed.length > 255) {
    throw validationError('Title must be 255 characters or less');
  }

  return trimmed;
}

/**
 * Validate URL
 */
function validateUrl(url) {
  if (!url) return null;

  if (typeof url !== 'string') {
    throw validationError('URL must be a string');
  }

  const trimmed = url.trim();

  if (!validator.isURL(trimmed, {
    protocols: ['http', 'https'],
    require_protocol: true,
  })) {
    throw validationError('Invalid URL format');
  }

  if (trimmed.length > 2048) {
    throw validationError('URL is too long (max 2048 characters)');
  }

  return trimmed;
}

/**
 * Validate text content
 */
function validateText(text, maxLength = 10000) {
  if (!text) return null;

  if (typeof text !== 'string') {
    throw validationError('Text must be a string');
  }

  const trimmed = text.trim();

  if (trimmed.length === 0) {
    return null;
  }

  if (trimmed.length > maxLength) {
    throw validationError(`Text must be ${maxLength} characters or less`);
  }

  return trimmed;
}

/**
 * Sanitize HTML content
 * Allows only safe tags for formatting
 */
function sanitizeContent(html) {
  if (!html) return '';

  return sanitizeHtml(html, {
    allowedTags: ['p', 'br', 'b', 'i', 'em', 'strong', 'a', 'code', 'pre', 'ul', 'ol', 'li'],
    allowedAttributes: {
      'a': ['href'],
    },
    allowedSchemes: ['http', 'https'],
  });
}

/**
 * Validate story type
 */
function validateStoryType(type) {
  const validTypes = ['story', 'ask', 'show', 'job', 'poll'];

  if (!type) return 'story';

  if (!validTypes.includes(type)) {
    throw validationError(`Story type must be one of: ${validTypes.join(', ')}`);
  }

  return type;
}

/**
 * Validate pagination parameters
 */
function validatePagination(page, limit) {
  const defaultPage = 1;
  const defaultLimit = 30;
  const maxLimit = 50;

  let validPage = parseInt(page) || defaultPage;
  let validLimit = parseInt(limit) || defaultLimit;

  if (validPage < 1) validPage = 1;
  if (validLimit < 1) validLimit = defaultLimit;
  if (validLimit > maxLimit) validLimit = maxLimit;

  return { page: validPage, limit: validLimit };
}

/**
 * Validate story submission
 * Must have either URL or text, not both
 */
function validateStorySubmission(data) {
  const { title, url, text, type } = data;

  const validatedTitle = validateTitle(title);
  const validatedUrl = validateUrl(url);
  const validatedText = validateText(text);
  const validatedType = validateStoryType(type);

  // Must have either URL or text
  if (!validatedUrl && !validatedText) {
    throw validationError('Story must have either a URL or text content');
  }

  // Cannot have both URL and text (for link posts)
  if (validatedUrl && validatedText) {
    throw validationError('Story cannot have both URL and text content');
  }

  return {
    title: validatedTitle,
    url: validatedUrl,
    text: validatedText ? sanitizeContent(validatedText) : null,
    type: validatedType,
  };
}

/**
 * Validate comment submission
 */
function validateCommentSubmission(data) {
  const { text, parentId } = data;

  const validatedText = validateText(text, 10000);

  if (!validatedText) {
    throw validationError('Comment text is required');
  }

  const validatedParentId = parentId ? parseInt(parentId) : null;

  if (parentId && isNaN(validatedParentId)) {
    throw validationError('Invalid parent comment ID');
  }

  return {
    text: sanitizeContent(validatedText),
    parentId: validatedParentId,
  };
}

module.exports = {
  validateUsername,
  validateEmail,
  validatePassword,
  validateTitle,
  validateUrl,
  validateText,
  sanitizeContent,
  validateStoryType,
  validatePagination,
  validateStorySubmission,
  validateCommentSubmission,
};
