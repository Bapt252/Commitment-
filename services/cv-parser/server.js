const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const multer = require('multer');
const winston = require('winston');
const { Pool } = require('pg');
const redis = require('redis');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5051;

// Logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'cv-parser' },
  transports: [
    new winston.transports.File({ filename: '/var/log/app/error.log', level: 'error' }),
    new winston.transports.File({ filename: '/var/log/app/combined.log' }),
    new winston.transports.Console()
  ]
});

// Database
const db = new Pool({
  connectionString: process.env.POSTGRES_URL
});

// Redis
const redisClient = redis.createClient({
  url: process.env.REDIS_URL
});
redisClient.connect();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// File upload
const upload = multer({
  dest: '/tmp/uploads',
  limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10485760 }
});

// Health check
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    await redisClient.ping();
    res.json({
      status: 'healthy',
      service: 'cv-parser',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});

// CV parsing endpoint
app.post('/api/parse', upload.single('cv'), async (req, res) => {
  try {
    logger.info('CV parsing request received');
    res.json({
      message: 'CV parsing service ready',
      file: req.file?.originalname,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('CV parsing error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`🔍 CV Parser Service running on port ${PORT}`);
});

module.exports = app;