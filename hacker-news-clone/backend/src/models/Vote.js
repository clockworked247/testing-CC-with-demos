const { query, transaction } = require('../config/database');
const { duplicateError, forbiddenError, notFoundError } = require('../utils/errors');
const { calculateVoteWeight } = require('../utils/ranking');
const User = require('./User');
const Story = require('./Story');
const Comment = require('./Comment');

class Vote {
  /**
   * Vote on a story
   */
  static async voteOnStory(userId, storyId) {
    return await transaction(async (client) => {
      // Get user for karma calculation
      const user = await User.findById(userId);
      if (!user) {
        throw notFoundError('User not found');
      }

      // Get story
      const story = await Story.findById(storyId);
      if (!story) {
        throw notFoundError('Story not found');
      }

      // Cannot vote on own content
      if (story.user_id === userId) {
        throw forbiddenError('Cannot vote on your own content');
      }

      // Check if already voted
      const existingVote = await client.query(
        'SELECT id FROM votes WHERE user_id = $1 AND story_id = $2',
        [userId, storyId]
      );

      if (existingVote.rows.length > 0) {
        throw duplicateError('You have already voted on this story');
      }

      // Calculate vote weight based on karma
      const voteWeight = calculateVoteWeight(user);

      // Create vote
      await client.query(
        'INSERT INTO votes (user_id, story_id, vote_weight) VALUES ($1, $2, $3)',
        [userId, storyId, voteWeight]
      );

      // Update story points
      const result = await client.query(
        'UPDATE stories SET points = points + $1 WHERE id = $2 RETURNING points',
        [voteWeight, storyId]
      );

      // Update story author's karma
      await client.query(
        'UPDATE users SET karma = karma + 1 WHERE id = $1',
        [story.user_id]
      );

      return {
        points: result.rows[0].points,
        voteWeight,
      };
    });
  }

  /**
   * Unvote on a story
   */
  static async unvoteOnStory(userId, storyId) {
    return await transaction(async (client) => {
      // Get existing vote
      const voteResult = await client.query(
        'SELECT vote_weight FROM votes WHERE user_id = $1 AND story_id = $2',
        [userId, storyId]
      );

      if (voteResult.rows.length === 0) {
        throw notFoundError('Vote not found');
      }

      const voteWeight = voteResult.rows[0].vote_weight;

      // Delete vote
      await client.query(
        'DELETE FROM votes WHERE user_id = $1 AND story_id = $2',
        [userId, storyId]
      );

      // Update story points
      const result = await client.query(
        'UPDATE stories SET points = points - $1 WHERE id = $2 RETURNING points, user_id',
        [voteWeight, storyId]
      );

      const story = result.rows[0];

      // Update story author's karma
      await client.query(
        'UPDATE users SET karma = karma - 1 WHERE id = $1',
        [story.user_id]
      );

      return {
        points: story.points,
        voteWeight,
      };
    });
  }

  /**
   * Vote on a comment
   */
  static async voteOnComment(userId, commentId) {
    return await transaction(async (client) => {
      // Get user for karma calculation
      const user = await User.findById(userId);
      if (!user) {
        throw notFoundError('User not found');
      }

      // Check karma requirement for voting on comments
      if (user.karma < 50) {
        throw forbiddenError('You need at least 50 karma to vote on comments');
      }

      // Get comment
      const comment = await Comment.findById(commentId);
      if (!comment) {
        throw notFoundError('Comment not found');
      }

      // Cannot vote on own content
      if (comment.user_id === userId) {
        throw forbiddenError('Cannot vote on your own content');
      }

      // Check if already voted
      const existingVote = await client.query(
        'SELECT id FROM votes WHERE user_id = $1 AND comment_id = $2',
        [userId, commentId]
      );

      if (existingVote.rows.length > 0) {
        throw duplicateError('You have already voted on this comment');
      }

      // Calculate vote weight based on karma
      const voteWeight = calculateVoteWeight(user);

      // Create vote
      await client.query(
        'INSERT INTO votes (user_id, comment_id, vote_weight) VALUES ($1, $2, $3)',
        [userId, commentId, voteWeight]
      );

      // Update comment points
      const result = await client.query(
        'UPDATE comments SET points = points + $1 WHERE id = $2 RETURNING points',
        [voteWeight, commentId]
      );

      // Update comment author's karma
      await client.query(
        'UPDATE users SET karma = karma + 1 WHERE id = $1',
        [comment.user_id]
      );

      return {
        points: result.rows[0].points,
        voteWeight,
      };
    });
  }

  /**
   * Unvote on a comment
   */
  static async unvoteOnComment(userId, commentId) {
    return await transaction(async (client) => {
      // Get existing vote
      const voteResult = await client.query(
        'SELECT vote_weight FROM votes WHERE user_id = $1 AND comment_id = $2',
        [userId, commentId]
      );

      if (voteResult.rows.length === 0) {
        throw notFoundError('Vote not found');
      }

      const voteWeight = voteResult.rows[0].vote_weight;

      // Delete vote
      await client.query(
        'DELETE FROM votes WHERE user_id = $1 AND comment_id = $2',
        [userId, commentId]
      );

      // Update comment points
      const result = await client.query(
        'UPDATE comments SET points = points - $1 WHERE id = $2 RETURNING points, user_id',
        [voteWeight, commentId]
      );

      const comment = result.rows[0];

      // Update comment author's karma
      await client.query(
        'UPDATE users SET karma = karma - 1 WHERE id = $1',
        [comment.user_id]
      );

      return {
        points: comment.points,
        voteWeight,
      };
    });
  }

  /**
   * Check if user has voted on a story
   */
  static async hasVotedOnStory(userId, storyId) {
    const result = await query(
      'SELECT id FROM votes WHERE user_id = $1 AND story_id = $2',
      [userId, storyId]
    );

    return result.rows.length > 0;
  }

  /**
   * Check if user has voted on a comment
   */
  static async hasVotedOnComment(userId, commentId) {
    const result = await query(
      'SELECT id FROM votes WHERE user_id = $1 AND comment_id = $2',
      [userId, commentId]
    );

    return result.rows.length > 0;
  }

  /**
   * Get user's votes
   */
  static async getUserVotes(userId) {
    const result = await query(
      `SELECT
         'story' as type,
         story_id as id,
         vote_weight,
         created_at
       FROM votes
       WHERE user_id = $1 AND story_id IS NOT NULL
       UNION ALL
       SELECT
         'comment' as type,
         comment_id as id,
         vote_weight,
         created_at
       FROM votes
       WHERE user_id = $1 AND comment_id IS NOT NULL
       ORDER BY created_at DESC`,
      [userId]
    );

    return result.rows;
  }
}

module.exports = Vote;
