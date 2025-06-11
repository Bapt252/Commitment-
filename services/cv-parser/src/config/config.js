/**
 * Configuration for CV Parser Ultra v2.0
 * PROMPT 2: Centralized config for all services and integrations
 */

require('dotenv').config();

const config = {
  // Server configuration
  server: {
    port: process.env.PORT || 5051,
    host: process.env.HOST || '0.0.0.0',
    environment: process.env.NODE_ENV || 'development'
  },

  // OpenAI configuration for AI-powered extraction
  openai: {
    apiKey: process.env.OPENAI_API_KEY || 'your-openai-api-key',
    model: process.env.OPENAI_MODEL || 'gpt-4',
    maxTokens: parseInt(process.env.OPENAI_MAX_TOKENS) || 2000,
    temperature: parseFloat(process.env.OPENAI_TEMPERATURE) || 0.1,
    timeout: parseInt(process.env.OPENAI_TIMEOUT) || 30000
  },

  // Redis configuration for intelligent caching
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    password: process.env.REDIS_PASSWORD || '',
    database: parseInt(process.env.REDIS_DATABASE) || 0,
    keyPrefix: process.env.REDIS_KEY_PREFIX || 'cv_parser:',
    ttl: {
      parsing: parseInt(process.env.REDIS_TTL_PARSING) || 3600, // 1 hour
      session: parseInt(process.env.REDIS_TTL_SESSION) || 86400, // 24 hours
      validation: parseInt(process.env.REDIS_TTL_VALIDATION) || 1800 // 30 minutes
    }
  },

  // PostgreSQL configuration
  postgres: {
    url: process.env.POSTGRES_URL || 'postgresql://ssm_user:password@localhost:5432/cv_parser_db',
    pool: {
      min: parseInt(process.env.POSTGRES_POOL_MIN) || 2,
      max: parseInt(process.env.POSTGRES_POOL_MAX) || 10,
      idleTimeoutMillis: parseInt(process.env.POSTGRES_IDLE_TIMEOUT) || 30000,
      connectionTimeoutMillis: parseInt(process.env.POSTGRES_CONNECTION_TIMEOUT) || 2000
    }
  },

  // MinIO configuration for file storage
  minio: {
    endpoint: process.env.MINIO_ENDPOINT || 'localhost',
    port: parseInt(process.env.MINIO_PORT) || 9000,
    useSSL: process.env.MINIO_USE_SSL === 'true',
    accessKey: process.env.MINIO_ACCESS_KEY || 'minioadmin',
    secretKey: process.env.MINIO_SECRET_KEY || 'minioadmin',
    buckets: {
      cv: process.env.MINIO_BUCKET_CV || 'cv-documents',
      temp: process.env.MINIO_BUCKET_TEMP || 'temp-uploads'
    }
  },

  // File processing configuration
  files: {
    maxSize: parseInt(process.env.MAX_FILE_SIZE) || 10485760, // 10MB
    supportedFormats: (process.env.SUPPORTED_FORMATS || 'pdf,doc,docx,txt,jpg,jpeg,png').split(','),
    uploadPath: process.env.UPLOAD_PATH || '/tmp/uploads',
    cleanupInterval: parseInt(process.env.CLEANUP_INTERVAL) || 3600000 // 1 hour
  },

  // OCR configuration
  ocr: {
    enabled: process.env.ENABLE_OCR === 'true',
    engine: process.env.OCR_ENGINE || 'tesseract',
    languages: (process.env.OCR_LANGUAGES || 'fra+eng').split('+'),
    confidence: parseFloat(process.env.OCR_CONFIDENCE) || 0.8,
    preprocessing: {
      resize: process.env.OCR_RESIZE === 'true',
      grayscale: process.env.OCR_GRAYSCALE === 'true',
      normalize: process.env.OCR_NORMALIZE === 'true',
      sharpen: process.env.OCR_SHARPEN === 'true'
    }
  },

  // WebSocket configuration for real-time streaming
  websocket: {
    enabled: process.env.ENABLE_WEBSOCKETS !== 'false',
    pingTimeout: parseInt(process.env.WS_PING_TIMEOUT) || 60000,
    pingInterval: parseInt(process.env.WS_PING_INTERVAL) || 25000,
    maxBufferSize: parseInt(process.env.WS_MAX_BUFFER_SIZE) || 100 * 1024 * 1024, // 100MB
    compression: process.env.WS_COMPRESSION === 'true',
    heartbeat: {
      enabled: process.env.WS_HEARTBEAT_ENABLED !== 'false',
      interval: parseInt(process.env.WS_HEARTBEAT_INTERVAL) || 30000
    }
  },

  // CORS configuration
  cors: {
    origins: process.env.CORS_ORIGINS ? 
      process.env.CORS_ORIGINS.split(',') : 
      ['http://localhost:3000', 'http://localhost:8080'],
    credentials: process.env.CORS_CREDENTIALS !== 'false',
    maxAge: parseInt(process.env.CORS_MAX_AGE) || 86400
  },

  // Authentication & Security
  auth: {
    jwtSecret: process.env.JWT_SECRET || 'your-jwt-secret-key',
    jwtExpiry: process.env.JWT_EXPIRY || '24h',
    apiKeyHeader: process.env.API_KEY_HEADER || 'x-api-key',
    rateLimiting: {
      enabled: process.env.RATE_LIMITING_ENABLED !== 'false',
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 900000, // 15 minutes
      max: parseInt(process.env.RATE_LIMIT_MAX) || 100,
      skipSuccessfulRequests: process.env.RATE_LIMIT_SKIP_SUCCESS === 'true'
    }
  },

  // Monitoring & Metrics
  monitoring: {
    prometheus: {
      enabled: process.env.PROMETHEUS_ENABLED !== 'false',
      endpoint: process.env.PROMETHEUS_ENDPOINT || '/metrics',
      prefix: process.env.PROMETHEUS_PREFIX || 'cv_parser_'
    },
    logging: {
      level: process.env.LOG_LEVEL || 'info',
      format: process.env.LOG_FORMAT || 'json',
      file: process.env.LOG_FILE || '/var/log/app/cv-parser.log',
      maxFiles: parseInt(process.env.LOG_MAX_FILES) || 10,
      maxSize: process.env.LOG_MAX_SIZE || '10m'
    },
    health: {
      endpoint: process.env.HEALTH_ENDPOINT || '/health',
      interval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000
    }
  },

  // Performance targets (PROMPT 2 objectives)
  targets: {
    parsing: {
      maxDuration: parseInt(process.env.TARGET_PARSING_DURATION) || 3000, // 3 seconds
      textRecognitionAccuracy: parseFloat(process.env.TARGET_TEXT_ACCURACY) || 0.995, // 99.5%
      extractionAccuracy: parseFloat(process.env.TARGET_EXTRACTION_ACCURACY) || 0.98, // 98%
      throughput: parseInt(process.env.TARGET_THROUGHPUT) || 1000 // 1000 CV/min
    },
    cache: {
      hitRatio: parseFloat(process.env.TARGET_CACHE_HIT_RATIO) || 0.85, // 85%
      responseTime: parseInt(process.env.TARGET_CACHE_RESPONSE) || 50 // 50ms
    },
    websocket: {
      firstResponseTime: parseInt(process.env.TARGET_WS_FIRST_RESPONSE) || 500, // 500ms
      maxConnections: parseInt(process.env.TARGET_WS_MAX_CONNECTIONS) || 1000
    },
    user: {
      satisfactionScore: parseFloat(process.env.TARGET_USER_SATISFACTION) || 0.95, // 95%
      fallbackRate: parseFloat(process.env.TARGET_FALLBACK_RATE) || 0.005, // 0.5%
      validationWithoutCorrections: parseFloat(process.env.TARGET_VALIDATION_SUCCESS) || 0.95 // 95%
    },
    system: {
      availability: parseFloat(process.env.TARGET_AVAILABILITY) || 0.999, // 99.9%
      errorRate: parseFloat(process.env.TARGET_ERROR_RATE) || 0.001, // 0.1%
      cpuUsage: parseFloat(process.env.TARGET_CPU_USAGE) || 0.8, // 80%
      memoryUsage: parseFloat(process.env.TARGET_MEMORY_USAGE) || 0.8 // 80%
    }
  },

  // Feature flags
  features: {
    aiEnhancement: process.env.FEATURE_AI_ENHANCEMENT !== 'false',
    ocrFallback: process.env.FEATURE_OCR_FALLBACK !== 'false',
    intelligentCaching: process.env.FEATURE_INTELLIGENT_CACHING !== 'false',
    realTimeValidation: process.env.FEATURE_REALTIME_VALIDATION !== 'false',
    manualFallback: process.env.FEATURE_MANUAL_FALLBACK !== 'false',
    advancedAnalytics: process.env.FEATURE_ADVANCED_ANALYTICS !== 'false',
    betaFeatures: process.env.FEATURE_BETA_ENABLED === 'true'
  },

  // External services integration
  external: {
    apiGateway: {
      url: process.env.API_GATEWAY_URL || 'http://api-gateway:5050',
      timeout: parseInt(process.env.API_GATEWAY_TIMEOUT) || 10000
    },
    matchingService: {
      url: process.env.MATCHING_SERVICE_URL || 'http://matching-service:5052',
      timeout: parseInt(process.env.MATCHING_SERVICE_TIMEOUT) || 15000
    },
    userService: {
      url: process.env.USER_SERVICE_URL || 'http://user-service:5054',
      timeout: parseInt(process.env.USER_SERVICE_TIMEOUT) || 5000
    },
    notificationService: {
      url: process.env.NOTIFICATION_SERVICE_URL || 'http://notification-service:5055',
      timeout: parseInt(process.env.NOTIFICATION_SERVICE_TIMEOUT) || 3000
    }
  },

  // Validation rules configuration
  validation: {
    strictMode: process.env.VALIDATION_STRICT_MODE === 'true',
    requiredFields: (process.env.VALIDATION_REQUIRED_FIELDS || 'personal.firstName,personal.lastName,personal.email').split(','),
    maxCorrections: parseInt(process.env.VALIDATION_MAX_CORRECTIONS) || 10,
    confidenceThreshold: parseFloat(process.env.VALIDATION_CONFIDENCE_THRESHOLD) || 0.85,
    autoValidation: process.env.VALIDATION_AUTO_ENABLED !== 'false'
  },

  // Development & Testing
  development: {
    debugMode: process.env.DEBUG_MODE === 'true',
    mockAI: process.env.MOCK_AI_RESPONSES === 'true',
    seedData: process.env.SEED_TEST_DATA === 'true',
    verboseLogging: process.env.VERBOSE_LOGGING === 'true',
    skipAuthentication: process.env.SKIP_AUTH === 'true'
  }
};

// Validation function for required configuration
function validateConfig() {
  const required = [
    'OPENAI_API_KEY',
    'REDIS_URL',
    'POSTGRES_URL'
  ];

  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }

  // Validate numeric ranges
  if (config.targets.parsing.maxDuration > 10000) {
    throw new Error('Parsing duration target cannot exceed 10 seconds');
  }

  if (config.targets.cache.hitRatio < 0 || config.targets.cache.hitRatio > 1) {
    throw new Error('Cache hit ratio must be between 0 and 1');
  }

  // Validate file size limits
  if (config.files.maxSize > 50 * 1024 * 1024) { // 50MB
    throw new Error('Maximum file size cannot exceed 50MB');
  }
}

// Environment-specific overrides
if (config.server.environment === 'production') {
  // Production-specific settings
  config.monitoring.logging.level = 'warn';
  config.development.debugMode = false;
  config.development.mockAI = false;
  config.validation.strictMode = true;
  
  // Validate production requirements
  validateConfig();
} else if (config.server.environment === 'test') {
  // Test-specific settings
  config.redis.database = 1; // Use different Redis database for tests
  config.development.mockAI = true;
  config.files.maxSize = 1024 * 1024; // 1MB for tests
  config.ocr.enabled = false; // Disable OCR in tests
}

module.exports = config;
