const Story = require('../models/Story');
const Comment = require('../models/Comment');
const { validateStorySubmission, validatePagination, validateText } = require('../utils/validation');
const { notFoundError, forbiddenError } = require('../utils/errors');
const { asyncHandler } = require('../utils/errors');
const { calculateRank, calculateBestScore } = require('../utils/ranking');
const { cache } = require('../config/redis');

/**
 * Get stories list
 * GET /api/stories
 */
exports.getStories = asyncHandler(async (req, res) => {
  const { type = 'top', page, limit } = req.query;
  const { page: validPage, limit: validLimit } = validatePagination(page, limit);
  const userId = req.user ? req.user.id : null;

  // Try to get from cache
  const cacheKey = `stories:${type}:page:${validPage}:limit:${validLimit}:user:${userId || 'anon'}`;
  const cached = await cache.get(cacheKey);

  if (cached) {
    return res.json(cached);
  }

  // Get stories from database
  const result = await Story.getStories({
    type,
    page: validPage,
    limit: validLimit,
    userId,
  });

  let { stories } = result;
  const { pagination } = result;

  // Apply ranking algorithm for 'top' type
  if (type === 'top') {
    stories = stories.map(story => ({
      ...story,
      rank: calculateRank(story),
    })).sort((a, b) => b.rank - a.rank);
  }

  // Apply best score for 'best' type
  if (type === 'best') {
    stories = stories.map(story => ({
      ...story,
      bestScore: calculateBestScore(story),
    })).sort((a, b) => b.bestScore - a.bestScore);
  }

  const response = {
    stories,
    pagination,
  };

  // Cache the result
  const ttl = type === 'new' ? 30 : type === 'top' ? 60 : 300;
  await cache.set(cacheKey, response, ttl);

  res.json(response);
});

/**
 * Get single story with comments
 * GET /api/stories/:id
 */
exports.getStory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user ? req.user.id : null;

  // Try to get from cache
  const cacheKey = `story:${id}:user:${userId || 'anon'}`;
  const cached = await cache.get(cacheKey);

  if (cached) {
    return res.json(cached);
  }

  const story = await Story.findById(id);

  if (!story) {
    throw notFoundError('Story not found');
  }

  // Get nested comments
  const comments = await Comment.getNestedComments(id, userId);

  const response = {
    story,
    comments,
  };

  // Cache for 30 seconds
  await cache.set(cacheKey, response, 30);

  res.json(response);
});

/**
 * Create a new story
 * POST /api/stories
 */
exports.createStory = asyncHandler(async (req, res) => {
  const { title, url, text, type } = req.body;
  const userId = req.user.id;

  // Validate submission
  const validated = validateStorySubmission({ title, url, text, type });

  // Create story
  const story = await Story.create({
    ...validated,
    userId,
  });

  // Invalidate cache
  await cache.invalidatePattern('stories:*');

  res.status(201).json({
    message: 'Story created successfully',
    story,
  });
});

/**
 * Update a story
 * PUT /api/stories/:id
 */
exports.updateStory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { text } = req.body;
  const userId = req.user.id;

  // Validate text
  const validatedText = validateText(text, 10000);

  if (!validatedText) {
    throw validationError('Text is required');
  }

  // Check if user can edit
  const canEdit = await Story.canEdit(id, userId);

  if (!canEdit && !req.user.is_moderator) {
    throw forbiddenError('You do not have permission to edit this story');
  }

  // Update story
  const story = await Story.update(id, { text: validatedText });

  // Invalidate cache
  await cache.invalidatePattern(`story:${id}:*`);
  await cache.invalidatePattern('stories:*');

  res.json({
    message: 'Story updated successfully',
    story,
  });
});

/**
 * Delete a story
 * DELETE /api/stories/:id
 */
exports.deleteStory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const story = await Story.findById(id);

  if (!story) {
    throw notFoundError('Story not found');
  }

  // Check permissions
  if (story.user_id !== userId && !req.user.is_moderator) {
    throw forbiddenError('You do not have permission to delete this story');
  }

  await Story.delete(id);

  // Invalidate cache
  await cache.invalidatePattern(`story:${id}:*`);
  await cache.invalidatePattern('stories:*');

  res.json({
    message: 'Story deleted successfully',
  });
});

/**
 * Toggle save story
 * POST /api/stories/:id/save
 */
exports.toggleSaveStory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const story = await Story.findById(id);

  if (!story) {
    throw notFoundError('Story not found');
  }

  const result = await Story.toggleSave(id, userId);

  res.json({
    message: result.saved ? 'Story saved' : 'Story unsaved',
    saved: result.saved,
  });
});
