const express = require('express');
const router = express.Router();
const commitmentController = require('../controllers/commitmentController');
const { protect } = require('../middleware/auth');

// Public routes
router.get('/public', commitmentController.getPublic);

// Protected routes
router.post('/', protect, commitmentController.create);
router.get('/', protect, commitmentController.getAllForUser);
router.get('/:id', protect, commitmentController.getById);
router.put('/:id', protect, commitmentController.update);
router.delete('/:id', protect, commitmentController.delete);
router.post('/:id/checkpoints', protect, commitmentController.addCheckpoint);

module.exports = router;