/**
 * CV Parser Ultra v2.0 - Main Server
 * Real-time streaming with WebSocket, OpenAI integration, interactive validation
 * 
 * PROMPT 2 Features:
 * ✅ Streaming temps réel avec WebSocket
 * ✅ Support OpenAI API sécurisé côté serveur
 * ✅ Validation interactive des données extraites
 * ✅ Fallback manuel si parsing insatisfaisant
 * ✅ Multi-formats: PDF, DOCX, DOC, JPG, PNG jusqu'à 10MB
 * ✅ Cache Redis intelligent
 * ✅ OCR haute performance
 * ✅ Intégration complète avec infrastructure existante
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;

// Configuration
const config = require('./config/config');
const logger = require('./utils/logger');

// Services
const ParsingService = require('./services/ParsingService');
const WebSocketService = require('./services/WebSocketService');
const CacheService = require('./services/CacheService');
const ValidationService = require('./services/ValidationService');
const MetricsService = require('./services/MetricsService');

// Routes
const cvRoutes = require('./routes/cvRoutes');
const healthRoutes = require('./routes/healthRoutes');
const validationRoutes = require('./routes/validationRoutes');

// Middleware
const errorHandler = require('./middleware/errorHandler');
const authMiddleware = require('./middleware/authMiddleware');
const uploadMiddleware = require('./middleware/uploadMiddleware');

const app = express();
const server = http.createServer(app);

class CVParserServer {
  constructor() {
    this.app = app;
    this.server = server;
    this.io = null;
    this.services = {};
    this.isReady = false;
  }

  async initialize() {
    try {
      logger.info('🚀 CV Parser Ultra v2.0 starting...');

      // Initialize services
      await this.initializeServices();
      
      // Configure Express
      this.configureExpress();
      
      // Initialize WebSocket
      this.initializeWebSocket();
      
      // Configure routes
      this.configureRoutes();
      
      // Configure error handling
      this.configureErrorHandling();
      
      this.isReady = true;
      logger.info('✅ CV Parser Ultra v2.0 initialized successfully');
      
    } catch (error) {
      logger.error('❌ Failed to initialize CV Parser Ultra v2.0:', error);
      throw error;
    }
  }

  async initializeServices() {
    logger.info('📦 Initializing services...');

    // Cache Service (Redis)
    this.services.cache = new CacheService(config.redis);
    await this.services.cache.connect();

    // Parsing Service (Core AI + OCR)
    this.services.parsing = new ParsingService({
      openai: config.openai,
      cache: this.services.cache,
      storage: config.minio
    });

    // Validation Service
    this.services.validation = new ValidationService({
      cache: this.services.cache
    });

    // Metrics Service (Prometheus)
    this.services.metrics = new MetricsService();

    logger.info('✅ All services initialized');
  }

  configureExpress() {
    // Security
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"]
        }
      }
    }));

    // CORS
    this.app.use(cors({
      origin: config.cors.origins,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      allowedHeaders: ['Content-Type', 'Authorization', 'x-task-id']
    }));

    // Compression
    this.app.use(compression());

    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: {
        error: 'Too many requests from this IP, please try again later.'
      },
      standardHeaders: true,
      legacyHeaders: false
    });
    this.app.use(limiter);

    // Body parsing
    this.app.use(express.json({ limit: '50mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));

    // Request logging
    this.app.use((req, res, next) => {
      logger.info(`${req.method} ${req.path}`, {
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        taskId: req.headers['x-task-id']
      });
      next();
    });

    // Metrics collection
    this.app.use((req, res, next) => {
      const start = Date.now();
      res.on('finish', () => {
        const duration = Date.now() - start;
        this.services.metrics.recordHttpRequest(req.method, req.route?.path || req.path, res.statusCode, duration);
      });
      next();
    });
  }

  initializeWebSocket() {
    this.io = socketIo(this.server, {
      cors: {
        origin: config.cors.origins,
        methods: ["GET", "POST"],
        credentials: true
      },
      maxHttpBufferSize: 1e8, // 100MB for large file uploads
      pingTimeout: 60000,
      pingInterval: 25000
    });

    // Initialize WebSocket service
    this.services.websocket = new WebSocketService(this.io, {
      parsing: this.services.parsing,
      validation: this.services.validation,
      cache: this.services.cache,
      metrics: this.services.metrics
    });

    logger.info('🔌 WebSocket server initialized');
  }

  configureRoutes() {
    // Health check
    this.app.use('/health', healthRoutes);

    // API routes with authentication
    this.app.use('/api/v2/parse/cv', authMiddleware, cvRoutes(this.services));
    this.app.use('/api/v2/parse/validate', authMiddleware, validationRoutes(this.services));

    // Metrics endpoint
    this.app.get('/metrics', async (req, res) => {
      try {
        const metrics = await this.services.metrics.getPrometheusMetrics();
        res.set('Content-Type', 'text/plain');
        res.send(metrics);
      } catch (error) {
        logger.error('Failed to get metrics:', error);
        res.status(500).json({ error: 'Failed to get metrics' });
      }
    });

    // API documentation
    this.app.get('/api/v2/docs', (req, res) => {
      res.json({
        service: 'CV Parser Ultra v2.0',
        version: '2.0.0',
        endpoints: {
          'POST /api/v2/parse/cv/stream': 'Parse CV with real-time streaming',
          'WS /api/v2/parse/status/{taskId}': 'WebSocket for progress tracking',
          'GET /api/v2/parse/validate/{taskId}': 'Interactive validation',
          'PUT /api/v2/parse/corrections/{taskId}': 'Submit user corrections',
          'GET /health': 'Health check',
          'GET /metrics': 'Prometheus metrics'
        },
        features: [
          'Real-time streaming with WebSocket',
          'OpenAI-powered extraction',
          'Interactive validation',
          'Intelligent caching',
          'High-performance OCR',
          'Multi-format support (PDF, DOCX, DOC, JPG, PNG)'
        ]
      });
    });

    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        service: 'SuperSmartMatch CV Parser Ultra v2.0',
        status: this.isReady ? 'ready' : 'initializing',
        version: '2.0.0',
        timestamp: new Date().toISOString(),
        documentation: '/api/v2/docs'
      });
    });
  }

  configureErrorHandling() {
    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Endpoint not found',
        message: `${req.method} ${req.originalUrl} is not a valid endpoint`,
        documentation: '/api/v2/docs'
      });
    });

    // Global error handler
    this.app.use(errorHandler);

    // Graceful shutdown
    process.on('SIGTERM', () => this.shutdown('SIGTERM'));
    process.on('SIGINT', () => this.shutdown('SIGINT'));
    
    // Uncaught exception handler
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught Exception:', error);
      this.shutdown('uncaughtException');
    });

    // Unhandled rejection handler
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
      this.shutdown('unhandledRejection');
    });
  }

  async start() {
    try {
      await this.initialize();
      
      const port = config.server.port || 5051;
      this.server.listen(port, () => {
        logger.info(`🎯 CV Parser Ultra v2.0 running on port ${port}`);
        logger.info(`📊 Metrics available at http://localhost:${port}/metrics`);
        logger.info(`📚 API docs at http://localhost:${port}/api/v2/docs`);
        logger.info(`🔌 WebSocket ready for real-time streaming`);
        logger.info('🚀 PROMPT 2 features fully operational!');
      });

    } catch (error) {
      logger.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  async shutdown(signal) {
    logger.info(`📥 Received ${signal}. Graceful shutdown starting...`);

    try {
      // Close server
      this.server.close(() => {
        logger.info('🔌 HTTP server closed');
      });

      // Close WebSocket connections
      if (this.io) {
        this.io.close();
        logger.info('📡 WebSocket server closed');
      }

      // Close services
      if (this.services.cache) {
        await this.services.cache.disconnect();
        logger.info('💾 Cache service disconnected');
      }

      logger.info('✅ Graceful shutdown completed');
      process.exit(0);

    } catch (error) {
      logger.error('❌ Error during shutdown:', error);
      process.exit(1);
    }
  }
}

// Start the server if this file is run directly
if (require.main === module) {
  const server = new CVParserServer();
  server.start().catch((error) => {
    logger.error('Failed to start CV Parser Ultra v2.0:', error);
    process.exit(1);
  });
}

module.exports = CVParserServer;
