const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const { authenticate } = require('../middleware/auth');

// User profile routes
router.get('/:username', userController.getUserProfile);
router.put('/:username', authenticate, userController.updateProfile);

// User's saved items (private)
router.get('/:username/saved', authenticate, userController.getSavedItems);

// User's submissions and comments
router.get('/:username/submissions', userController.getUserSubmissions);
router.get('/:username/comments', userController.getUserComments);

module.exports = router;
