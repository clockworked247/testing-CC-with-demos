const Comment = require('../models/Comment');
const Story = require('../models/Story');
const { validateCommentSubmission, validateText } = require('../utils/validation');
const { notFoundError, forbiddenError } = require('../utils/errors');
const { asyncHandler } = require('../utils/errors');
const { cache } = require('../config/redis');

/**
 * Get comments for a story
 * GET /api/stories/:storyId/comments
 */
exports.getComments = asyncHandler(async (req, res) => {
  const { storyId } = req.params;
  const userId = req.user ? req.user.id : null;

  const comments = await Comment.getNestedComments(storyId, userId);

  res.json({
    comments,
  });
});

/**
 * Create a new comment
 * POST /api/stories/:storyId/comments
 */
exports.createComment = asyncHandler(async (req, res) => {
  const { storyId } = req.params;
  const { text, parentId } = req.body;
  const userId = req.user.id;

  // Validate comment
  const validated = validateCommentSubmission({ text, parentId });

  // Check if story exists
  const story = await Story.findById(storyId);
  if (!story) {
    throw notFoundError('Story not found');
  }

  // Create comment
  const comment = await Comment.create({
    storyId,
    userId,
    ...validated,
  });

  // Invalidate cache
  await cache.invalidatePattern(`story:${storyId}:*`);

  res.status(201).json({
    message: 'Comment created successfully',
    comment,
  });
});

/**
 * Update a comment
 * PUT /api/comments/:id
 */
exports.updateComment = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { text } = req.body;
  const userId = req.user.id;

  // Validate text
  const validatedText = validateText(text, 10000);

  if (!validatedText) {
    throw validationError('Text is required');
  }

  // Check if user can edit
  const canEdit = await Comment.canEdit(id, userId);

  if (!canEdit && !req.user.is_moderator) {
    throw forbiddenError('You do not have permission to edit this comment');
  }

  // Update comment
  const comment = await Comment.update(id, { text: validatedText });

  // Invalidate cache
  await cache.invalidatePattern(`story:${comment.story_id}:*`);

  res.json({
    message: 'Comment updated successfully',
    comment,
  });
});

/**
 * Delete a comment
 * DELETE /api/comments/:id
 */
exports.deleteComment = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const comment = await Comment.findById(id);

  if (!comment) {
    throw notFoundError('Comment not found');
  }

  // Check permissions
  if (comment.user_id !== userId && !req.user.is_moderator) {
    throw forbiddenError('You do not have permission to delete this comment');
  }

  await Comment.delete(id);

  // Invalidate cache
  await cache.invalidatePattern(`story:${comment.story_id}:*`);

  res.json({
    message: 'Comment deleted successfully',
  });
});

/**
 * Get comment thread
 * GET /api/comments/:id/thread
 */
exports.getThread = asyncHandler(async (req, res) => {
  const { id } = req.params;

  const thread = await Comment.getThread(id);

  res.json({
    thread,
  });
});

/**
 * Toggle save comment
 * POST /api/comments/:id/save
 */
exports.toggleSaveComment = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const comment = await Comment.findById(id);

  if (!comment) {
    throw notFoundError('Comment not found');
  }

  const result = await Comment.toggleSave(id, userId);

  res.json({
    message: result.saved ? 'Comment saved' : 'Comment unsaved',
    saved: result.saved,
  });
});
