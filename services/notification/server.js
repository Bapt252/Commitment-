const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const winston = require('winston');
const { Pool } = require('pg');
const redis = require('redis');
const { Server } = require('socket.io');
const http = require('http');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });
const PORT = process.env.PORT || 5055;

// Logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  defaultMeta: { service: 'notification' },
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

// WebSocket connection handling
io.on('connection', (socket) => {
  logger.info(`WebSocket client connected: ${socket.id}`);
  
  socket.on('disconnect', () => {
    logger.info(`WebSocket client disconnected: ${socket.id}`);
  });
});

// Health check
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    await redisClient.ping();
    res.json({ status: 'healthy', service: 'notification', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: error.message });
  }
});

// Notification endpoints
app.post('/api/send', async (req, res) => {
  try {
    logger.info('Send notification request received');
    // Emit to all connected clients
    io.emit('notification', { message: 'New notification', timestamp: new Date().toISOString() });
    res.json({ message: 'Notification sent', timestamp: new Date().toISOString() });
  } catch (error) {
    logger.error('Send notification error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/notifications/:userId', async (req, res) => {
  try {
    res.json({ notifications: [], total: 0, userId: req.params.userId });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

server.listen(PORT, '0.0.0.0', () => {
  logger.info(`🔔 Notification Service running on port ${PORT}`);
});

module.exports = app;