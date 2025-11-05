/**
 * WebSocket Service for real-time updates
 */

let io;

/**
 * Initialize socket service with io instance
 */
function init(ioInstance) {
  io = ioInstance;
}

/**
 * Emit story points update
 */
function emitStoryPointsUpdate(storyId, points) {
  if (!io) return;

  io.to(`story-${storyId}`).emit('story-points-updated', {
    storyId,
    points,
  });
}

/**
 * Emit new comment
 */
function emitNewComment(storyId, comment) {
  if (!io) return;

  io.to(`story-${storyId}`).emit('comment-added', {
    storyId,
    comment,
  });
}

/**
 * Emit comment points update
 */
function emitCommentPointsUpdate(storyId, commentId, points) {
  if (!io) return;

  io.to(`story-${storyId}`).emit('comment-points-updated', {
    storyId,
    commentId,
    points,
  });
}

/**
 * Emit comment deleted
 */
function emitCommentDeleted(storyId, commentId) {
  if (!io) return;

  io.to(`story-${storyId}`).emit('comment-deleted', {
    storyId,
    commentId,
  });
}

/**
 * Emit story deleted
 */
function emitStoryDeleted(storyId) {
  if (!io) return;

  io.to(`story-${storyId}`).emit('story-deleted', {
    storyId,
  });
}

module.exports = {
  init,
  emitStoryPointsUpdate,
  emitNewComment,
  emitCommentPointsUpdate,
  emitCommentDeleted,
  emitStoryDeleted,
};
