const { query, transaction } = require('../config/database');
const { notFoundError, forbiddenError, validationError } = require('../utils/errors');

const MAX_DEPTH = 10;

class Comment {
  /**
   * Create a new comment
   */
  static async create({ storyId, userId, text, parentId = null }) {
    return await transaction(async (client) => {
      let path = '/';
      let depth = 0;

      // If this is a reply, get parent info
      if (parentId) {
        const parentResult = await client.query(
          'SELECT path, depth FROM comments WHERE id = $1',
          [parentId]
        );

        if (parentResult.rows.length === 0) {
          throw notFoundError('Parent comment not found');
        }

        const parent = parentResult.rows[0];
        depth = parent.depth + 1;

        if (depth > MAX_DEPTH) {
          throw validationError(`Maximum nesting depth (${MAX_DEPTH}) exceeded`);
        }

        path = `${parent.path}${parentId}/`;
      }

      // Insert comment
      const result = await client.query(
        `INSERT INTO comments (story_id, user_id, text, parent_id, path, depth)
         VALUES ($1, $2, $3, $4, $5, $6)
         RETURNING *`,
        [storyId, userId, text, parentId, path, depth]
      );

      // Update story comment count
      await client.query(
        'UPDATE stories SET comment_count = comment_count + 1 WHERE id = $1',
        [storyId]
      );

      return result.rows[0];
    });
  }

  /**
   * Find comment by ID
   */
  static async findById(id, includeDeleted = false) {
    const deletedCondition = includeDeleted ? '' : 'AND c.is_deleted = FALSE';

    const result = await query(
      `SELECT c.*, u.username, u.karma as user_karma
       FROM comments c
       JOIN users u ON c.user_id = u.id
       WHERE c.id = $1 ${deletedCondition}`,
      [id]
    );

    return result.rows[0] || null;
  }

  /**
   * Get all comments for a story (flat list)
   */
  static async getByStory(storyId, userId = null) {
    const result = await query(
      `SELECT
         c.*,
         u.username,
         u.karma as user_karma,
         ${userId ? `EXISTS(SELECT 1 FROM votes WHERE user_id = $2 AND comment_id = c.id) as user_voted` : 'FALSE as user_voted'}
       FROM comments c
       JOIN users u ON c.user_id = u.id
       WHERE c.story_id = $1 AND c.is_deleted = FALSE
       ORDER BY c.path`,
      userId ? [storyId, userId] : [storyId]
    );

    return result.rows;
  }

  /**
   * Get nested comment tree for a story
   */
  static async getNestedComments(storyId, userId = null) {
    const comments = await this.getByStory(storyId, userId);

    // Build nested structure
    const commentMap = new Map();
    const rootComments = [];

    // First pass: create map
    comments.forEach(comment => {
      comment.children = [];
      commentMap.set(comment.id, comment);
    });

    // Second pass: build tree
    comments.forEach(comment => {
      if (comment.parent_id === null) {
        rootComments.push(comment);
      } else {
        const parent = commentMap.get(comment.parent_id);
        if (parent) {
          parent.children.push(comment);
        }
      }
    });

    return rootComments;
  }

  /**
   * Get comment thread (comment and all its ancestors)
   */
  static async getThread(commentId) {
    const comment = await this.findById(commentId);

    if (!comment) {
      throw notFoundError('Comment not found');
    }

    // Get all ancestors using path
    const pathIds = comment.path
      .split('/')
      .filter(id => id !== '')
      .map(id => parseInt(id));

    if (pathIds.length === 0) {
      return [comment];
    }

    const result = await query(
      `SELECT c.*, u.username
       FROM comments c
       JOIN users u ON c.user_id = u.id
       WHERE c.id = ANY($1)
       ORDER BY c.depth`,
      [pathIds]
    );

    return [...result.rows, comment];
  }

  /**
   * Update comment
   */
  static async update(id, { text }) {
    const result = await query(
      `UPDATE comments
       SET text = $1, updated_at = CURRENT_TIMESTAMP
       WHERE id = $2 AND is_deleted = FALSE
       RETURNING *`,
      [text, id]
    );

    if (result.rows.length === 0) {
      throw notFoundError('Comment not found');
    }

    return result.rows[0];
  }

  /**
   * Delete comment (soft delete)
   */
  static async delete(id) {
    return await transaction(async (client) => {
      const result = await client.query(
        `UPDATE comments
         SET is_deleted = TRUE, text = '[deleted]', updated_at = CURRENT_TIMESTAMP
         WHERE id = $1
         RETURNING story_id`,
        [id]
      );

      if (result.rows.length === 0) {
        throw notFoundError('Comment not found');
      }

      const { story_id } = result.rows[0];

      // Decrement story comment count
      await client.query(
        'UPDATE stories SET comment_count = comment_count - 1 WHERE id = $1',
        [story_id]
      );

      return result.rows[0];
    });
  }

  /**
   * Update comment points
   */
  static async updatePoints(commentId, delta) {
    const result = await query(
      `UPDATE comments
       SET points = points + $1
       WHERE id = $2
       RETURNING points`,
      [delta, commentId]
    );

    return result.rows[0];
  }

  /**
   * Check if user can edit comment
   */
  static async canEdit(commentId, userId) {
    const comment = await this.findById(commentId);

    if (!comment) {
      throw notFoundError('Comment not found');
    }

    // Check if comment is within edit window (2 hours)
    const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000);
    const createdAt = new Date(comment.created_at);

    if (createdAt < twoHoursAgo) {
      throw forbiddenError('Edit window has expired (2 hours)');
    }

    return comment.user_id === userId;
  }

  /**
   * Get reply count for a comment
   */
  static async getReplyCount(commentId) {
    const result = await query(
      `SELECT COUNT(*) as count
       FROM comments
       WHERE parent_id = $1 AND is_deleted = FALSE`,
      [commentId]
    );

    return parseInt(result.rows[0].count);
  }

  /**
   * Get recent comments by user
   */
  static async getByUser(username, limit = 30) {
    const result = await query(
      `SELECT c.*, u.username, s.title as story_title
       FROM comments c
       JOIN users u ON c.user_id = u.id
       JOIN stories s ON c.story_id = s.id
       WHERE u.username = $1 AND c.is_deleted = FALSE
       ORDER BY c.created_at DESC
       LIMIT $2`,
      [username, limit]
    );

    return result.rows;
  }

  /**
   * Save/unsave comment for user
   */
  static async toggleSave(commentId, userId) {
    // Check if already saved
    const existing = await query(
      'SELECT id FROM saved_items WHERE user_id = $1 AND comment_id = $2',
      [userId, commentId]
    );

    if (existing.rows.length > 0) {
      // Unsave
      await query(
        'DELETE FROM saved_items WHERE user_id = $1 AND comment_id = $2',
        [userId, commentId]
      );
      return { saved: false };
    } else {
      // Save
      await query(
        'INSERT INTO saved_items (user_id, comment_id) VALUES ($1, $2)',
        [userId, commentId]
      );
      return { saved: true };
    }
  }
}

module.exports = Comment;
