const express = require('express');
const router = express.Router();
const storyController = require('../controllers/storyController');
const commentController = require('../controllers/commentController');
const voteController = require('../controllers/voteController');
const { authenticate, optionalAuth } = require('../middleware/auth');
const { storySubmitLimiter, commentLimiter, voteLimiter } = require('../middleware/rateLimiter');

// Story routes
router.get('/', optionalAuth, storyController.getStories);
router.get('/:id', optionalAuth, storyController.getStory);
router.post('/', authenticate, storySubmitLimiter, storyController.createStory);
router.put('/:id', authenticate, storyController.updateStory);
router.delete('/:id', authenticate, storyController.deleteStory);

// Save/unsave story
router.post('/:id/save', authenticate, storyController.toggleSaveStory);

// Comments on stories
router.get('/:storyId/comments', optionalAuth, commentController.getComments);
router.post('/:storyId/comments', authenticate, commentLimiter, commentController.createComment);

// Voting on stories
router.post('/:id/vote', authenticate, voteLimiter, voteController.voteOnStory);
router.delete('/:id/vote', authenticate, voteController.unvoteOnStory);

module.exports = router;
