const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const winston = require('winston');
const { Pool } = require('pg');
const redis = require('redis');
const client = require('prom-client');
const cron = require('node-cron');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5056;

// Prometheus metrics
const register = new client.Registry();
client.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'status_code']
});
register.registerMetric(httpRequestDuration);

// Logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  defaultMeta: { service: 'analytics' },
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

// Metrics middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.observe({ method: req.method, status_code: res.statusCode }, duration);
  });
  next();
});

// Health check
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    await redisClient.ping();
    res.json({ status: 'healthy', service: 'analytics', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: error.message });
  }
});

// Metrics endpoint for Prometheus
app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (error) {
    res.status(500).end(error);
  }
});

// Analytics endpoints
app.get('/api/stats', async (req, res) => {
  try {
    res.json({
      totalUsers: 0,
      totalJobs: 0,
      totalMatches: 0,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/dashboard', async (req, res) => {
  try {
    res.json({
      message: 'Analytics dashboard data ready',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Scheduled analytics tasks
cron.schedule('*/5 * * * *', () => {
  logger.info('Running scheduled analytics aggregation');
  // Add aggregation logic here
});

app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`📊 Analytics Service running on port ${PORT}`);
});

module.exports = app;