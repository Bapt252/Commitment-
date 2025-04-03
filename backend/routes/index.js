const express = require('express');
const router = express.Router();
const userRoutes = require('./userRoutes');
const commitmentRoutes = require('./commitmentRoutes');

// Mount routes
router.use('/api/users', userRoutes);
router.use('/api/commitments', commitmentRoutes);

// Root route
router.get('/', (req, res) => {
  res.json({ message: 'Welcome to Commitment- API' });
});

module.exports = router;