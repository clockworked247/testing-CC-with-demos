const Vote = require('../models/Vote');
const { asyncHandler } = require('../utils/errors');
const { cache } = require('../config/redis');

/**
 * Vote on a story
 * POST /api/stories/:id/vote
 */
exports.voteOnStory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const result = await Vote.voteOnStory(userId, id);

  // Invalidate cache
  await cache.invalidatePattern(`story:${id}:*`);
  await cache.invalidatePattern('stories:*');

  res.json({
    message: 'Vote recorded successfully',
    points: result.points,
    voteWeight: result.voteWeight,
  });
});

/**
 * Unvote on a story
 * DELETE /api/stories/:id/vote
 */
exports.unvoteOnStory = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const result = await Vote.unvoteOnStory(userId, id);

  // Invalidate cache
  await cache.invalidatePattern(`story:${id}:*`);
  await cache.invalidatePattern('stories:*');

  res.json({
    message: 'Vote removed successfully',
    points: result.points,
  });
});

/**
 * Vote on a comment
 * POST /api/comments/:id/vote
 */
exports.voteOnComment = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const result = await Vote.voteOnComment(userId, id);

  res.json({
    message: 'Vote recorded successfully',
    points: result.points,
    voteWeight: result.voteWeight,
  });
});

/**
 * Unvote on a comment
 * DELETE /api/comments/:id/vote
 */
exports.unvoteOnComment = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;

  const result = await Vote.unvoteOnComment(userId, id);

  res.json({
    message: 'Vote removed successfully',
    points: result.points,
  });
});
