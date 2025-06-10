const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const slowDown = require('express-slow-down');
const { createProxyMiddleware } = require('http-proxy-middleware');
const jwt = require('jsonwebtoken');
const redis = require('redis');
const winston = require('winston');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5050;

// ===========================================
// LOGGING CONFIGURATION
// ===========================================
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'api-gateway' },
  transports: [
    new winston.transports.File({ 
      filename: '/var/log/app/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: '/var/log/app/combined.log' 
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// ===========================================
// REDIS CONNECTION
// ===========================================
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => {
  logger.error('Redis connection error:', err);
});

redisClient.on('connect', () => {
  logger.info('Connected to Redis');
});

redisClient.connect();

// ===========================================
// MIDDLEWARE CONFIGURATION
// ===========================================

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Compression
app.use(compression());

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Rate limiting
if (process.env.RATE_LIMIT_ENABLED === 'true') {
  const limiter = rateLimit({
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 15 * 60 * 1000,
    max: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    message: {
      error: 'Too many requests from this IP, please try again later.',
      retryAfter: Math.ceil((parseInt(process.env.RATE_LIMIT_WINDOW) || 15 * 60 * 1000) / 1000)
    },
    standardHeaders: true,
    legacyHeaders: false,
  });

  const speedLimiter = slowDown({
    windowMs: 15 * 60 * 1000,
    delayAfter: 50,
    delayMs: 500
  });

  app.use('/api', limiter);
  app.use('/api', speedLimiter);
}

// Request logging
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path} - IP: ${req.ip}`);
  next();
});

// ===========================================
// JWT MIDDLEWARE
// ===========================================
const authenticateJWT = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token is required' });
  }

  try {
    // Check if token is blacklisted
    const blacklisted = await redisClient.get(`blacklist:${token}`);
    if (blacklisted) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    logger.error('JWT verification failed:', error.message);
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
};

// ===========================================
// HEALTH CHECK ENDPOINT
// ===========================================
app.get('/health', async (req, res) => {
  try {
    // Check Redis connection
    await redisClient.ping();
    
    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'api-gateway',
      version: '2.0.0',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      dependencies: {
        redis: 'connected'
      }
    });
  } catch (error) {
    logger.error('Health check failed:', error);
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// ===========================================
// PROXY CONFIGURATION FOR MICROSERVICES
// ===========================================

// CV Parser Service
app.use('/api/cv', authenticateJWT, createProxyMiddleware({
  target: process.env.CV_PARSER_URL || 'http://localhost:5051',
  changeOrigin: true,
  pathRewrite: {
    '^/api/cv': '/api'
  },
  onError: (err, req, res) => {
    logger.error('CV Parser Service proxy error:', err.message);
    res.status(503).json({ error: 'CV Parser Service unavailable' });
  }
}));

// Job Parser Service
app.use('/api/jobs', authenticateJWT, createProxyMiddleware({
  target: process.env.JOB_PARSER_URL || 'http://localhost:5053',
  changeOrigin: true,
  pathRewrite: {
    '^/api/jobs': '/api'
  },
  onError: (err, req, res) => {
    logger.error('Job Parser Service proxy error:', err.message);
    res.status(503).json({ error: 'Job Parser Service unavailable' });
  }
}));

// Matching Service
app.use('/api/matching', authenticateJWT, createProxyMiddleware({
  target: process.env.MATCHING_SERVICE_URL || 'http://localhost:5052',
  changeOrigin: true,
  pathRewrite: {
    '^/api/matching': '/api'
  },
  onError: (err, req, res) => {
    logger.error('Matching Service proxy error:', err.message);
    res.status(503).json({ error: 'Matching Service unavailable' });
  }
}));

// User Service (some endpoints don't need auth)
app.use('/api/auth', createProxyMiddleware({
  target: process.env.USER_SERVICE_URL || 'http://localhost:5054',
  changeOrigin: true,
  pathRewrite: {
    '^/api/auth': '/api/auth'
  },
  onError: (err, req, res) => {
    logger.error('User Service proxy error:', err.message);
    res.status(503).json({ error: 'User Service unavailable' });
  }
}));

app.use('/api/users', authenticateJWT, createProxyMiddleware({
  target: process.env.USER_SERVICE_URL || 'http://localhost:5054',
  changeOrigin: true,
  pathRewrite: {
    '^/api/users': '/api/users'
  },
  onError: (err, req, res) => {
    logger.error('User Service proxy error:', err.message);
    res.status(503).json({ error: 'User Service unavailable' });
  }
}));

// Notification Service
app.use('/api/notifications', authenticateJWT, createProxyMiddleware({
  target: process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:5055',
  changeOrigin: true,
  pathRewrite: {
    '^/api/notifications': '/api'
  },
  onError: (err, req, res) => {
    logger.error('Notification Service proxy error:', err.message);
    res.status(503).json({ error: 'Notification Service unavailable' });
  }
}));

// Analytics Service
app.use('/api/analytics', authenticateJWT, createProxyMiddleware({
  target: process.env.ANALYTICS_SERVICE_URL || 'http://localhost:5056',
  changeOrigin: true,
  pathRewrite: {
    '^/api/analytics': '/api'
  },
  onError: (err, req, res) => {
    logger.error('Analytics Service proxy error:', err.message);
    res.status(503).json({ error: 'Analytics Service unavailable' });
  }
}));

// ===========================================
// AUTHENTICATION ENDPOINTS
// ===========================================

// Token validation endpoint
app.post('/api/validate-token', authenticateJWT, (req, res) => {
  res.json({
    valid: true,
    user: req.user,
    iat: req.user.iat,
    exp: req.user.exp
  });
});

// Token refresh endpoint
app.post('/api/refresh-token', authenticateJWT, (req, res) => {
  const newToken = jwt.sign(
    {
      userId: req.user.userId,
      email: req.user.email,
      role: req.user.role
    },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRY || '24h' }
  );

  res.json({ token: newToken });
});

// Logout endpoint (blacklist token)
app.post('/api/logout', authenticateJWT, async (req, res) => {
  try {
    const token = req.headers.authorization.split(' ')[1];
    const decoded = jwt.decode(token);
    const expiresIn = decoded.exp - Math.floor(Date.now() / 1000);
    
    // Add token to blacklist
    await redisClient.setEx(`blacklist:${token}`, expiresIn, 'true');
    
    res.json({ message: 'Successfully logged out' });
  } catch (error) {
    logger.error('Logout error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ===========================================
// ERROR HANDLING
// ===========================================

// 404 handler
app.use((req, res) => {
  logger.warn(`404 - Route not found: ${req.method} ${req.path}`);
  res.status(404).json({
    error: 'Route not found',
    method: req.method,
    path: req.path,
    timestamp: new Date().toISOString()
  });
});

// Global error handler
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', {
    error: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method
  });

  res.status(error.status || 500).json({
    error: process.env.NODE_ENV === 'production' 
      ? 'Internal server error' 
      : error.message,
    timestamp: new Date().toISOString()
  });
});

// ===========================================
// SERVER STARTUP
// ===========================================
const server = app.listen(PORT, '0.0.0.0', () => {
  logger.info(`🚀 SuperSmartMatch API Gateway running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV}`);
  logger.info(`JWT Secret configured: ${!!process.env.JWT_SECRET}`);
  logger.info(`Redis URL: ${process.env.REDIS_URL}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(async () => {
    await redisClient.quit();
    logger.info('Process terminated');
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully');
  server.close(async () => {
    await redisClient.quit();
    logger.info('Process terminated');
    process.exit(0);
  });
});

module.exports = app;