const { query, transaction } = require('../config/database');
const { notFoundError, duplicateError, forbiddenError } = require('../utils/errors');
const { normalizeURL, extractDomain, calculateSimilarity } = require('../utils/ranking');

class Story {
  /**
   * Create a new story
   */
  static async create({ title, url, text, type, userId }) {
    const normalizedUrl = url ? normalizeURL(url) : null;
    const domain = url ? extractDomain(url) : null;

    // Check for duplicates if URL provided
    if (normalizedUrl) {
      const duplicate = await this.findDuplicateUrl(normalizedUrl);
      if (duplicate) {
        throw duplicateError(`This URL was already submitted: ${duplicate.title}`);
      }
    }

    const result = await query(
      `INSERT INTO stories (title, url, text, story_type, user_id, domain)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [title, normalizedUrl, text, type, userId, domain]
    );

    return result.rows[0];
  }

  /**
   * Find duplicate URL (within last 7 days)
   */
  static async findDuplicateUrl(normalizedUrl) {
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

    const result = await query(
      `SELECT id, title, url, created_at
       FROM stories
       WHERE url = $1 AND created_at > $2 AND is_deleted = FALSE
       LIMIT 1`,
      [normalizedUrl, sevenDaysAgo]
    );

    return result.rows[0] || null;
  }

  /**
   * Find similar URLs (Levenshtein distance check)
   */
  static async findSimilarUrls(url, domain) {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

    const result = await query(
      `SELECT id, title, url
       FROM stories
       WHERE domain = $1 AND created_at > $2 AND is_deleted = FALSE
       LIMIT 20`,
      [domain, oneDayAgo]
    );

    // Check similarity
    for (const story of result.rows) {
      const similarity = calculateSimilarity(normalizeURL(url), normalizeURL(story.url));
      if (similarity > 0.85) {
        return { ...story, similarity };
      }
    }

    return null;
  }

  /**
   * Find story by ID with author info
   */
  static async findById(id, includeDeleted = false) {
    const deletedCondition = includeDeleted ? '' : 'AND s.is_deleted = FALSE';

    const result = await query(
      `SELECT s.*, u.username, u.karma as user_karma
       FROM stories s
       JOIN users u ON s.user_id = u.id
       WHERE s.id = $1 ${deletedCondition}`,
      [id]
    );

    return result.rows[0] || null;
  }

  /**
   * Get stories with ranking
   */
  static async getStories({ type = 'top', page = 1, limit = 30, userId = null }) {
    const offset = (page - 1) * limit;

    let orderBy = 'ORDER BY s.created_at DESC';
    let whereConditions = ['s.is_deleted = FALSE', 's.is_dead = FALSE'];

    // Filter by story type
    if (type === 'ask') {
      whereConditions.push("s.story_type = 'ask'");
    } else if (type === 'show') {
      whereConditions.push("s.story_type = 'show'");
    } else if (type === 'job') {
      whereConditions.push("s.story_type = 'job'");
    }

    // Different ordering for different types
    if (type === 'new') {
      orderBy = 'ORDER BY s.created_at DESC';
    } else if (type === 'top') {
      // For "top", we'll calculate rank in the application layer
      orderBy = 'ORDER BY s.points DESC, s.created_at DESC';
    } else if (type === 'best') {
      // For "best", we'll calculate best score in the application layer
      orderBy = 'ORDER BY s.points DESC, s.comment_count DESC';
    }

    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';

    const result = await query(
      `SELECT
         s.*,
         u.username,
         u.karma as user_karma,
         ${userId ? `EXISTS(SELECT 1 FROM votes WHERE user_id = $3 AND story_id = s.id) as user_voted` : 'FALSE as user_voted'},
         ${userId ? `EXISTS(SELECT 1 FROM saved_items WHERE user_id = $3 AND story_id = s.id) as user_saved` : 'FALSE as user_saved'}
       FROM stories s
       JOIN users u ON s.user_id = u.id
       ${whereClause}
       ${orderBy}
       LIMIT $1 OFFSET $2`,
      userId ? [limit, offset, userId] : [limit, offset]
    );

    // Get total count for pagination
    const countResult = await query(
      `SELECT COUNT(*) as total
       FROM stories s
       ${whereClause}`
    );

    const total = parseInt(countResult.rows[0].total);
    const totalPages = Math.ceil(total / limit);

    return {
      stories: result.rows,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasMore: page < totalPages,
      },
    };
  }

  /**
   * Update story
   */
  static async update(id, { text }) {
    const result = await query(
      `UPDATE stories
       SET text = $1, updated_at = CURRENT_TIMESTAMP
       WHERE id = $2 AND is_deleted = FALSE
       RETURNING *`,
      [text, id]
    );

    if (result.rows.length === 0) {
      throw notFoundError('Story not found');
    }

    return result.rows[0];
  }

  /**
   * Delete story (soft delete)
   */
  static async delete(id) {
    const result = await query(
      `UPDATE stories
       SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
       WHERE id = $1
       RETURNING *`,
      [id]
    );

    if (result.rows.length === 0) {
      throw notFoundError('Story not found');
    }

    return result.rows[0];
  }

  /**
   * Increment comment count
   */
  static async incrementCommentCount(storyId, delta = 1) {
    await query(
      `UPDATE stories
       SET comment_count = comment_count + $1
       WHERE id = $2`,
      [delta, storyId]
    );
  }

  /**
   * Update story points
   */
  static async updatePoints(storyId, delta) {
    const result = await query(
      `UPDATE stories
       SET points = points + $1
       WHERE id = $2
       RETURNING points`,
      [delta, storyId]
    );

    return result.rows[0];
  }

  /**
   * Check if user can edit story
   */
  static async canEdit(storyId, userId) {
    const story = await this.findById(storyId);

    if (!story) {
      throw notFoundError('Story not found');
    }

    // Check if story is within edit window (2 hours)
    const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000);
    const createdAt = new Date(story.created_at);

    if (createdAt < twoHoursAgo) {
      throw forbiddenError('Edit window has expired (2 hours)');
    }

    return story.user_id === userId;
  }

  /**
   * Save/unsave story for user
   */
  static async toggleSave(storyId, userId) {
    // Check if already saved
    const existing = await query(
      'SELECT id FROM saved_items WHERE user_id = $1 AND story_id = $2',
      [userId, storyId]
    );

    if (existing.rows.length > 0) {
      // Unsave
      await query(
        'DELETE FROM saved_items WHERE user_id = $1 AND story_id = $2',
        [userId, storyId]
      );
      return { saved: false };
    } else {
      // Save
      await query(
        'INSERT INTO saved_items (user_id, story_id) VALUES ($1, $2)',
        [userId, storyId]
      );
      return { saved: true };
    }
  }

  /**
   * Get story count by user
   */
  static async getCountByUser(userId) {
    const result = await query(
      'SELECT COUNT(*) as count FROM stories WHERE user_id = $1 AND is_deleted = FALSE',
      [userId]
    );

    return parseInt(result.rows[0].count);
  }
}

module.exports = Story;
