const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const winston = require('winston');
const { Pool } = require('pg');
const redis = require('redis');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5052;

// Logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  defaultMeta: { service: 'matching' },
  transports: [
    new winston.transports.File({ filename: '/var/log/app/error.log', level: 'error' }),
    new winston.transports.File({ filename: '/var/log/app/combined.log' }),
    new winston.transports.Console()
  ]
});

// Database & Redis
const db = new Pool({ connectionString: process.env.POSTGRES_URL });
const redisClient = redis.createClient({ url: process.env.REDIS_URL });
redisClient.connect();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    await redisClient.ping();
    res.json({ status: 'healthy', service: 'matching', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: error.message });
  }
});

// Matching endpoints
app.post('/api/match', async (req, res) => {
  try {
    logger.info('Matching request received');
    res.json({ 
      message: 'Matching service ready', 
      algorithm: 'v2_optimized',
      timestamp: new Date().toISOString() 
    });
  } catch (error) {
    logger.error('Matching error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/matches/:userId', async (req, res) => {
  try {
    res.json({ matches: [], total: 0, userId: req.params.userId });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`🎯 Matching Service running on port ${PORT}`);
});

module.exports = app;