const bcrypt = require('bcrypt');
const { query, transaction } = require('../config/database');
const { duplicateError, notFoundError, accountLockedError } = require('../utils/errors');

const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS) || 10;
const MAX_LOGIN_ATTEMPTS = parseInt(process.env.MAX_LOGIN_ATTEMPTS) || 5;
const LOCK_TIME = parseInt(process.env.LOCK_TIME) || 15 * 60 * 1000; // 15 minutes

class User {
  /**
   * Create a new user
   */
  static async create({ username, email, password }) {
    // Hash password
    const password_hash = await bcrypt.hash(password, BCRYPT_ROUNDS);

    try {
      const result = await query(
        `INSERT INTO users (username, email, password_hash)
         VALUES ($1, $2, $3)
         RETURNING id, username, email, karma, created_at, email_verified`,
        [username, email, password_hash]
      );

      return result.rows[0];
    } catch (error) {
      // Handle unique constraint violations
      if (error.code === '23505') {
        if (error.constraint === 'users_username_key') {
          throw duplicateError('Username already exists');
        }
        if (error.constraint === 'users_email_key') {
          throw duplicateError('Email already exists');
        }
      }
      throw error;
    }
  }

  /**
   * Find user by ID
   */
  static async findById(id) {
    const result = await query(
      `SELECT id, username, email, karma, about, created_at, email_verified,
              is_moderator, is_shadowbanned
       FROM users
       WHERE id = $1`,
      [id]
    );

    return result.rows[0] || null;
  }

  /**
   * Find user by username
   */
  static async findByUsername(username) {
    const result = await query(
      `SELECT id, username, email, karma, about, created_at, email_verified,
              is_moderator, is_shadowbanned
       FROM users
       WHERE username = $1`,
      [username]
    );

    return result.rows[0] || null;
  }

  /**
   * Find user by email
   */
  static async findByEmail(email) {
    const result = await query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );

    return result.rows[0] || null;
  }

  /**
   * Authenticate user
   */
  static async authenticate(username, password) {
    const result = await query(
      `SELECT id, username, email, password_hash, karma, failed_login_attempts,
              locked_until, email_verified, is_shadowbanned
       FROM users
       WHERE username = $1`,
      [username]
    );

    if (result.rows.length === 0) {
      return null;
    }

    const user = result.rows[0];

    // Check if account is locked
    if (user.locked_until && new Date(user.locked_until) > new Date()) {
      const remainingTime = Math.ceil((new Date(user.locked_until) - new Date()) / 60000);
      throw accountLockedError(`Account is locked. Try again in ${remainingTime} minutes.`);
    }

    // Verify password
    const isValid = await bcrypt.compare(password, user.password_hash);

    if (!isValid) {
      // Increment failed login attempts
      await this.incrementFailedLogins(user.id);
      return null;
    }

    // Reset failed login attempts on successful login
    await this.resetFailedLogins(user.id);

    // Remove password hash before returning
    delete user.password_hash;

    return user;
  }

  /**
   * Increment failed login attempts
   */
  static async incrementFailedLogins(userId) {
    const result = await query(
      `UPDATE users
       SET failed_login_attempts = failed_login_attempts + 1,
           locked_until = CASE
             WHEN failed_login_attempts + 1 >= $1
             THEN NOW() + INTERVAL '${LOCK_TIME} milliseconds'
             ELSE locked_until
           END
       WHERE id = $2
       RETURNING failed_login_attempts`,
      [MAX_LOGIN_ATTEMPTS, userId]
    );

    return result.rows[0];
  }

  /**
   * Reset failed login attempts
   */
  static async resetFailedLogins(userId) {
    await query(
      'UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = $1',
      [userId]
    );
  }

  /**
   * Update user profile
   */
  static async update(userId, { about, email }) {
    const updates = [];
    const values = [];
    let paramCount = 1;

    if (about !== undefined) {
      updates.push(`about = $${paramCount++}`);
      values.push(about);
    }

    if (email !== undefined) {
      updates.push(`email = $${paramCount++}`);
      values.push(email);
    }

    if (updates.length === 0) {
      return await this.findById(userId);
    }

    values.push(userId);

    try {
      const result = await query(
        `UPDATE users
         SET ${updates.join(', ')}
         WHERE id = $${paramCount}
         RETURNING id, username, email, karma, about, created_at`,
        values
      );

      if (result.rows.length === 0) {
        throw notFoundError('User not found');
      }

      return result.rows[0];
    } catch (error) {
      if (error.code === '23505' && error.constraint === 'users_email_key') {
        throw duplicateError('Email already exists');
      }
      throw error;
    }
  }

  /**
   * Update user karma
   */
  static async updateKarma(userId, delta) {
    const result = await query(
      `UPDATE users
       SET karma = karma + $1
       WHERE id = $2
       RETURNING karma`,
      [delta, userId]
    );

    return result.rows[0];
  }

  /**
   * Verify user email
   */
  static async verifyEmail(userId) {
    await query(
      'UPDATE users SET email_verified = TRUE WHERE id = $1',
      [userId]
    );
  }

  /**
   * Get user submissions (stories)
   */
  static async getSubmissions(username, limit = 30) {
    const result = await query(
      `SELECT s.*, u.username
       FROM stories s
       JOIN users u ON s.user_id = u.id
       WHERE u.username = $1 AND s.is_deleted = FALSE
       ORDER BY s.created_at DESC
       LIMIT $2`,
      [username, limit]
    );

    return result.rows;
  }

  /**
   * Get user comments
   */
  static async getComments(username, limit = 30) {
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
   * Get user's saved items
   */
  static async getSavedItems(userId) {
    const result = await query(
      `SELECT
         'story' as type,
         s.id,
         s.title,
         s.url,
         s.points,
         s.comment_count,
         s.created_at,
         u.username as author
       FROM saved_items si
       JOIN stories s ON si.story_id = s.id
       JOIN users u ON s.user_id = u.id
       WHERE si.user_id = $1 AND s.is_deleted = FALSE
       UNION ALL
       SELECT
         'comment' as type,
         c.id,
         c.text as title,
         NULL as url,
         c.points,
         0 as comment_count,
         c.created_at,
         u.username as author
       FROM saved_items si
       JOIN comments c ON si.comment_id = c.id
       JOIN users u ON c.user_id = u.id
       WHERE si.user_id = $1 AND c.is_deleted = FALSE
       ORDER BY created_at DESC`,
      [userId]
    );

    return result.rows;
  }
}

module.exports = User;
