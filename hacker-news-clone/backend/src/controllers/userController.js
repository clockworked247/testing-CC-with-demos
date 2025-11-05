const User = require('../models/User');
const { validateText, validateEmail } = require('../utils/validation');
const { notFoundError, forbiddenError } = require('../utils/errors');
const { asyncHandler } = require('../utils/errors');
const { cache } = require('../config/redis');

/**
 * Get user profile
 * GET /api/users/:username
 */
exports.getUserProfile = asyncHandler(async (req, res) => {
  const { username } = req.params;

  // Try to get from cache
  const cacheKey = `user:${username}:profile`;
  const cached = await cache.get(cacheKey);

  if (cached) {
    return res.json(cached);
  }

  const user = await User.findByUsername(username);

  if (!user) {
    throw notFoundError('User not found');
  }

  // Get user's submissions and comments
  const submissions = await User.getSubmissions(username, 30);
  const comments = await User.getComments(username, 30);

  const response = {
    user: {
      username: user.username,
      karma: user.karma,
      about: user.about,
      created_at: user.created_at,
    },
    submissions,
    comments,
  };

  // Cache for 5 minutes
  await cache.set(cacheKey, response, 300);

  res.json(response);
});

/**
 * Update user profile
 * PUT /api/users/:username
 */
exports.updateProfile = asyncHandler(async (req, res) => {
  const { username } = req.params;
  const { about, email } = req.body;
  const userId = req.user.id;

  // Check if user is updating their own profile
  const user = await User.findByUsername(username);

  if (!user) {
    throw notFoundError('User not found');
  }

  if (user.id !== userId) {
    throw forbiddenError('You can only edit your own profile');
  }

  // Validate input
  const validatedAbout = about !== undefined ? validateText(about, 3000) : undefined;
  const validatedEmail = email !== undefined ? validateEmail(email) : undefined;

  // Update user
  const updatedUser = await User.update(userId, {
    about: validatedAbout,
    email: validatedEmail,
  });

  // Invalidate cache
  await cache.invalidatePattern(`user:${username}:*`);

  res.json({
    message: 'Profile updated successfully',
    user: {
      username: updatedUser.username,
      email: updatedUser.email,
      karma: updatedUser.karma,
      about: updatedUser.about,
    },
  });
});

/**
 * Get user's saved items
 * GET /api/users/:username/saved
 */
exports.getSavedItems = asyncHandler(async (req, res) => {
  const { username } = req.params;
  const userId = req.user.id;

  // Check if user is requesting their own saved items
  const user = await User.findByUsername(username);

  if (!user) {
    throw notFoundError('User not found');
  }

  if (user.id !== userId) {
    throw forbiddenError('You can only view your own saved items');
  }

  const savedItems = await User.getSavedItems(userId);

  res.json({
    savedItems,
  });
});

/**
 * Get user's submissions
 * GET /api/users/:username/submissions
 */
exports.getUserSubmissions = asyncHandler(async (req, res) => {
  const { username } = req.params;
  const { limit = 30 } = req.query;

  const submissions = await User.getSubmissions(username, parseInt(limit));

  res.json({
    submissions,
  });
});

/**
 * Get user's comments
 * GET /api/users/:username/comments
 */
exports.getUserComments = asyncHandler(async (req, res) => {
  const { username } = req.params;
  const { limit = 30 } = req.query;

  const comments = await User.getComments(username, parseInt(limit));

  res.json({
    comments,
  });
});
