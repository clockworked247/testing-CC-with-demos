const express = require('express');
const router = express.Router();
const commentController = require('../controllers/commentController');
const voteController = require('../controllers/voteController');
const { authenticate } = require('../middleware/auth');
const { voteLimiter } = require('../middleware/rateLimiter');

// Comment routes
router.get('/:id/thread', commentController.getThread);
router.put('/:id', authenticate, commentController.updateComment);
router.delete('/:id', authenticate, commentController.deleteComment);

// Save/unsave comment
router.post('/:id/save', authenticate, commentController.toggleSaveComment);

// Voting on comments
router.post('/:id/vote', authenticate, voteLimiter, voteController.voteOnComment);
router.delete('/:id/vote', authenticate, voteController.unvoteOnComment);

module.exports = router;
