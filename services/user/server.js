const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const winston = require('winston');
const { Pool } = require('pg');
const redis = require('redis');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5054;

// Logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  defaultMeta: { service: 'user' },
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
    res.json({ status: 'healthy', service: 'user', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: error.message });
  }
});

// Auth endpoints
app.post('/api/auth/login', async (req, res) => {
  try {
    logger.info('Login request received');
    const token = jwt.sign({ userId: 1, email: 'demo@example.com' }, process.env.JWT_SECRET || 'secret', { expiresIn: '24h' });
    res.json({ token, user: { id: 1, email: 'demo@example.com' } });
  } catch (error) {
    logger.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/auth/register', async (req, res) => {
  try {
    logger.info('Register request received');
    res.json({ message: 'User registration service ready', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/users/:id', async (req, res) => {
  try {
    res.json({ id: req.params.id, email: 'demo@example.com', createdAt: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`👤 User Service running on port ${PORT}`);
});

module.exports = app;