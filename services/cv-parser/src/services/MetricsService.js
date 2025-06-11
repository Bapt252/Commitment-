/**
 * Metrics Service - Prometheus monitoring for CV Parser Ultra v2.0
 * PROMPT 2: Real-time metrics dashboard with Grafana integration
 */

const promClient = require('prom-client');
const logger = require('../utils/logger');

class MetricsService {
  constructor() {
    // Initialize Prometheus registry
    this.register = new promClient.Registry();
    
    // Add default metrics (CPU, memory, etc.)
    promClient.collectDefaultMetrics({ 
      register: this.register,
      prefix: 'cv_parser_'
    });

    this.setupCustomMetrics();
    
    logger.info('📊 Metrics service initialized with Prometheus');
  }

  /**
   * Setup custom metrics for PROMPT 2 monitoring
   */
  setupCustomMetrics() {
    // ===========================================
    // PROMPT 2 CORE METRICS
    // ===========================================

    // Parsing duration (target: <3 seconds)
    this.parsingDuration = new promClient.Histogram({
      name: 'cv_parser_parsing_duration_seconds',
      help: 'Duration of CV parsing operations in seconds',
      labelNames: ['type', 'format', 'cache_status'],
      buckets: [0.5, 1, 2, 3, 5, 10, 15, 30]
    });

    // Parsing accuracy (target: 99.5% text recognition, 98% extraction)
    this.parsingAccuracy = new promClient.Gauge({
      name: 'cv_parser_parsing_accuracy_ratio',
      help: 'Accuracy ratio of CV parsing by field type',
      labelNames: ['field_type', 'extraction_method']
    });

    // WebSocket connections (real-time monitoring)
    this.websocketConnections = new promClient.Gauge({
      name: 'cv_parser_websocket_connections_active',
      help: 'Number of active WebSocket connections'
    });

    // Cache hit ratio (target: >85%)
    this.cacheHitRatio = new promClient.Gauge({
      name: 'cv_parser_cache_hit_ratio',
      help: 'Cache hit ratio for parser requests',
      labelNames: ['parser_type', 'cache_type']
    });

    // User satisfaction score (target: 95%+ validation without corrections)
    this.userSatisfactionScore = new promClient.Gauge({
      name: 'cv_parser_user_satisfaction_score',
      help: 'User satisfaction score based on corrections needed',
      labelNames: ['satisfaction_level']
    });

    // ===========================================
    // PERFORMANCE METRICS
    // ===========================================

    // HTTP request metrics
    this.httpRequestDuration = new promClient.Histogram({
      name: 'cv_parser_http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status_code'],
      buckets: [0.1, 0.5, 1, 2, 5, 10]
    });

    // HTTP request counter
    this.httpRequestTotal = new promClient.Counter({
      name: 'cv_parser_http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code']
    });

    // File processing metrics
    this.filesProcessed = new promClient.Counter({
      name: 'cv_parser_files_processed_total',
      help: 'Total number of files processed',
      labelNames: ['file_type', 'processing_status', 'extraction_method']
    });

    // OCR operations
    this.ocrOperations = new promClient.Counter({
      name: 'cv_parser_ocr_operations_total',
      help: 'Total number of OCR operations performed',
      labelNames: ['ocr_engine', 'language', 'success']
    });

    // AI API calls
    this.aiApiCalls = new promClient.Counter({
      name: 'cv_parser_ai_api_calls_total',
      help: 'Total number of AI API calls',
      labelNames: ['provider', 'model', 'success']
    });

    // ===========================================
    // BUSINESS METRICS  
    // ===========================================

    // Task completion rate
    this.taskCompletionRate = new promClient.Gauge({
      name: 'cv_parser_task_completion_rate',
      help: 'Percentage of tasks completed successfully'
    });

    // Manual fallback rate (target: <0.5%)
    this.fallbackRate = new promClient.Gauge({
      name: 'cv_parser_fallback_rate',
      help: 'Percentage of tasks requiring manual fallback'
    });

    // Validation metrics
    this.validationMetrics = new promClient.Counter({
      name: 'cv_parser_validation_events_total',
      help: 'Total validation events',
      labelNames: ['event_type', 'field_category']
    });

    // Correction metrics
    this.correctionMetrics = new promClient.Histogram({
      name: 'cv_parser_corrections_per_task',
      help: 'Number of corrections required per task',
      labelNames: ['correction_type'],
      buckets: [0, 1, 2, 3, 5, 10, 20]
    });

    // ===========================================
    // SYSTEM HEALTH METRICS
    // ===========================================

    // Service availability
    this.serviceAvailability = new promClient.Gauge({
      name: 'cv_parser_service_availability',
      help: 'Service availability status (1 = up, 0 = down)',
      labelNames: ['service_component']
    });

    // Error rate
    this.errorRate = new promClient.Gauge({
      name: 'cv_parser_error_rate',
      help: 'Error rate percentage',
      labelNames: ['error_type', 'component']
    });

    // Queue metrics
    this.queueMetrics = new promClient.Gauge({
      name: 'cv_parser_queue_size',
      help: 'Current queue size for processing',
      labelNames: ['queue_type']
    });

    // Register all metrics
    this.register.registerMetric(this.parsingDuration);
    this.register.registerMetric(this.parsingAccuracy);
    this.register.registerMetric(this.websocketConnections);
    this.register.registerMetric(this.cacheHitRatio);
    this.register.registerMetric(this.userSatisfactionScore);
    this.register.registerMetric(this.httpRequestDuration);
    this.register.registerMetric(this.httpRequestTotal);
    this.register.registerMetric(this.filesProcessed);
    this.register.registerMetric(this.ocrOperations);
    this.register.registerMetric(this.aiApiCalls);
    this.register.registerMetric(this.taskCompletionRate);
    this.register.registerMetric(this.fallbackRate);
    this.register.registerMetric(this.validationMetrics);
    this.register.registerMetric(this.correctionMetrics);
    this.register.registerMetric(this.serviceAvailability);
    this.register.registerMetric(this.errorRate);
    this.register.registerMetric(this.queueMetrics);
  }

  /**
   * Record HTTP request metrics
   */
  recordHttpRequest(method, route, statusCode, duration) {
    this.httpRequestTotal.inc({ method, route, status_code: statusCode });
    this.httpRequestDuration.observe({ method, route, status_code: statusCode }, duration / 1000);
  }

  /**
   * Record parsing operation metrics
   * PROMPT 2: Track <3 second target
   */
  recordParsingOperation(options = {}) {
    const { 
      duration, 
      fileType, 
      cacheHit = false, 
      extractionMethod = 'ai',
      success = true 
    } = options;

    const cacheStatus = cacheHit ? 'hit' : 'miss';
    
    this.parsingDuration.observe(
      { type: 'cv', format: fileType, cache_status: cacheStatus }, 
      duration / 1000
    );

    this.filesProcessed.inc({ 
      file_type: fileType, 
      processing_status: success ? 'success' : 'failed',
      extraction_method: extractionMethod
    });

    // Log if performance target not met
    if (duration > 3000 && !cacheHit) {
      logger.warn(`⚠️ Parsing duration exceeded target: ${duration}ms for ${fileType}`, {
        target: '3000ms',
        cacheHit,
        extractionMethod
      });
    }
  }

  /**
   * Record parsing accuracy
   * PROMPT 2: Track 99.5% text recognition, 98% extraction targets
   */
  recordParsingAccuracy(fieldType, accuracy, extractionMethod = 'ai') {
    this.parsingAccuracy.set(
      { field_type: fieldType, extraction_method: extractionMethod }, 
      accuracy
    );

    // Alert if accuracy below targets
    const targets = {
      'text_recognition': 0.995,
      'data_extraction': 0.98,
      'overall': 0.975
    };

    if (targets[fieldType] && accuracy < targets[fieldType]) {
      logger.warn(`⚠️ Accuracy below target for ${fieldType}`, {
        actual: accuracy,
        target: targets[fieldType],
        extractionMethod
      });
    }
  }

  /**
   * Record WebSocket connection metrics
   * PROMPT 2: Monitor real-time connections
   */
  recordWebSocketConnection() {
    this.websocketConnections.inc();
  }

  recordWebSocketDisconnection() {
    this.websocketConnections.dec();
  }

  /**
   * Record cache performance
   * PROMPT 2: Monitor 85%+ hit ratio target
   */
  recordCacheMetrics(parserType, hitRatio, cacheType = 'redis') {
    this.cacheHitRatio.set({ parser_type: parserType, cache_type: cacheType }, hitRatio);

    // Alert if cache hit ratio below target
    if (hitRatio < 0.85) {
      logger.warn(`⚠️ Cache hit ratio below target for ${parserType}`, {
        actual: hitRatio,
        target: 0.85,
        cacheType
      });
    }
  }

  /**
   * Record user satisfaction metrics
   * PROMPT 2: Monitor 95%+ satisfaction target
   */
  recordUserSatisfaction(satisfactionScore, level = 'overall') {
    this.userSatisfactionScore.set({ satisfaction_level: level }, satisfactionScore);

    // Alert if satisfaction below target
    if (satisfactionScore < 95) {
      logger.warn(`⚠️ User satisfaction below target`, {
        actual: satisfactionScore,
        target: 95,
        level
      });
    }
  }

  /**
   * Record OCR operation
   */
  recordOCROperation(engine = 'tesseract', language = 'eng', success = true) {
    this.ocrOperations.inc({ 
      ocr_engine: engine, 
      language, 
      success: success.toString() 
    });
  }

  /**
   * Record AI API call
   */
  recordAIApiCall(provider = 'openai', model = 'gpt-4', success = true) {
    this.aiApiCalls.inc({ 
      provider, 
      model, 
      success: success.toString() 
    });
  }

  /**
   * Record validation event
   */
  recordValidationEvent(eventType, fieldCategory = 'general') {
    this.validationMetrics.inc({ event_type: eventType, field_category: fieldCategory });
  }

  /**
   * Record corrections needed
   */
  recordCorrections(correctionsCount, correctionType = 'user') {
    this.correctionMetrics.observe({ correction_type: correctionType }, correctionsCount);
  }

  /**
   * Update business metrics
   * PROMPT 2: Track completion rate and fallback rate
   */
  updateBusinessMetrics(options = {}) {
    const { 
      completionRate, 
      fallbackRate, 
      errorRate 
    } = options;

    if (completionRate !== undefined) {
      this.taskCompletionRate.set(completionRate);
    }

    if (fallbackRate !== undefined) {
      this.fallbackRate.set(fallbackRate);
      
      // Alert if fallback rate above target (0.5%)
      if (fallbackRate > 0.005) {
        logger.warn(`⚠️ Fallback rate above target`, {
          actual: fallbackRate,
          target: 0.005
        });
      }
    }

    if (errorRate !== undefined) {
      this.errorRate.set({ error_type: 'general', component: 'parser' }, errorRate);
    }
  }

  /**
   * Update service availability
   */
  updateServiceAvailability(component, isAvailable) {
    this.serviceAvailability.set({ service_component: component }, isAvailable ? 1 : 0);
  }

  /**
   * Update queue metrics
   */
  updateQueueMetrics(queueType, size) {
    this.queueMetrics.set({ queue_type: queueType }, size);
  }

  /**
   * Get Prometheus metrics
   */
  async getPrometheusMetrics() {
    return this.register.metrics();
  }

  /**
   * Get human-readable metrics summary
   * PROMPT 2: Dashboard-friendly metrics
   */
  async getMetricsSummary() {
    const metrics = await this.register.getMetricsAsJSON();
    
    const summary = {
      timestamp: new Date().toISOString(),
      service: 'CV Parser Ultra v2.0',
      version: '2.0.0',
      performance: {
        parsing: {
          avgDuration: this.getMetricValue(metrics, 'cv_parser_parsing_duration_seconds'),
          accuracy: this.getMetricValue(metrics, 'cv_parser_parsing_accuracy_ratio'),
          filesProcessed: this.getMetricValue(metrics, 'cv_parser_files_processed_total')
        },
        cache: {
          hitRatio: this.getMetricValue(metrics, 'cv_parser_cache_hit_ratio'),
          status: this.getMetricValue(metrics, 'cv_parser_cache_hit_ratio') > 0.85 ? 'GOOD' : 'NEEDS_IMPROVEMENT'
        },
        websockets: {
          activeConnections: this.getMetricValue(metrics, 'cv_parser_websocket_connections_active')
        }
      },
      business: {
        userSatisfaction: {
          score: this.getMetricValue(metrics, 'cv_parser_user_satisfaction_score'),
          status: this.getMetricValue(metrics, 'cv_parser_user_satisfaction_score') >= 95 ? 'EXCELLENT' : 'GOOD'
        },
        completionRate: this.getMetricValue(metrics, 'cv_parser_task_completion_rate'),
        fallbackRate: this.getMetricValue(metrics, 'cv_parser_fallback_rate')
      },
      system: {
        availability: this.getMetricValue(metrics, 'cv_parser_service_availability'),
        errorRate: this.getMetricValue(metrics, 'cv_parser_error_rate'),
        queueSize: this.getMetricValue(metrics, 'cv_parser_queue_size')
      },
      targets: {
        parsingDuration: { target: 3, unit: 'seconds' },
        cacheHitRatio: { target: 85, unit: 'percent' },
        userSatisfaction: { target: 95, unit: 'percent' },
        fallbackRate: { target: 0.5, unit: 'percent' },
        accuracy: { target: 98, unit: 'percent' }
      }
    };

    return summary;
  }

  /**
   * Helper to extract metric value
   */
  getMetricValue(metrics, metricName) {
    const metric = metrics.find(m => m.name === metricName);
    if (!metric || !metric.values || metric.values.length === 0) {
      return 0;
    }
    
    // Return the first value or aggregate if multiple
    const values = metric.values.map(v => v.value);
    return values.length === 1 ? values[0] : values.reduce((a, b) => a + b, 0) / values.length;
  }

  /**
   * Health check for metrics service
   */
  async healthCheck() {
    try {
      const metricsCount = (await this.register.getMetricsAsJSON()).length;
      
      return {
        status: 'UP',
        metricsRegistered: metricsCount,
        registry: 'healthy'
      };
    } catch (error) {
      return {
        status: 'DOWN',
        error: error.message
      };
    }
  }

  /**
   * Reset all metrics (for testing)
   */
  resetMetrics() {
    this.register.resetMetrics();
    logger.info('📊 All metrics reset');
  }
}

module.exports = MetricsService;
