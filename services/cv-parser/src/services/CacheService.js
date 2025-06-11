/**
 * Cache Service - Intelligent Redis caching
 * PROMPT 2: 85%+ hit ratio target, avoid re-parsing identical documents
 */

const Redis = require('redis');
const crypto = require('crypto');
const logger = require('../utils/logger');

class CacheService {
  constructor(config) {
    this.config = config;
    this.client = null;
    this.isConnected = false;
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      errors: 0
    };
  }

  /**
   * Connect to Redis
   */
  async connect() {
    try {
      this.client = Redis.createClient({
        url: this.config.url,
        password: this.config.password,
        socket: {
          connectTimeout: 5000,
          lazyConnect: true,
          reconnectStrategy: (retries) => {
            if (retries > 10) return new Error('Too many retries');
            return Math.min(retries * 50, 1000);
          }
        },
        database: this.config.database || 0
      });

      // Event handlers
      this.client.on('error', (error) => {
        logger.error('Redis connection error:', error);
        this.stats.errors++;
        this.isConnected = false;
      });

      this.client.on('connect', () => {
        logger.info('🔗 Redis connected successfully');
        this.isConnected = true;
      });

      this.client.on('reconnecting', () => {
        logger.info('🔄 Redis reconnecting...');
        this.isConnected = false;
      });

      this.client.on('ready', () => {
        logger.info('✅ Redis client ready');
        this.isConnected = true;
      });

      await this.client.connect();
      
      // Test connection
      await this.client.ping();
      logger.info('📡 Redis cache service initialized');

    } catch (error) {
      logger.error('Failed to connect to Redis:', error);
      this.isConnected = false;
      throw error;
    }
  }

  /**
   * Disconnect from Redis
   */
  async disconnect() {
    if (this.client) {
      await this.client.disconnect();
      this.isConnected = false;
      logger.info('🔌 Redis disconnected');
    }
  }

  /**
   * Get value from cache
   * PROMPT 2: Intelligent caching for duplicate document detection
   */
  async get(key) {
    if (!this.isConnected) {
      logger.warn('Redis not connected, cache miss');
      this.stats.misses++;
      return null;
    }

    try {
      const value = await this.client.get(key);
      
      if (value !== null) {
        this.stats.hits++;
        logger.debug(`📥 Cache HIT for key: ${key}`);
        return JSON.parse(value);
      } else {
        this.stats.misses++;
        logger.debug(`📤 Cache MISS for key: ${key}`);
        return null;
      }
    } catch (error) {
      logger.error('Cache get error:', error);
      this.stats.errors++;
      this.stats.misses++;
      return null;
    }
  }

  /**
   * Set value in cache with expiration
   */
  async set(key, value, ttl = 3600) {
    if (!this.isConnected) {
      logger.warn('Redis not connected, skipping cache set');
      return false;
    }

    try {
      const serialized = JSON.stringify(value);
      await this.client.setEx(key, ttl, serialized);
      
      this.stats.sets++;
      logger.debug(`💾 Cache SET for key: ${key}, TTL: ${ttl}s`);
      return true;
    } catch (error) {
      logger.error('Cache set error:', error);
      this.stats.errors++;
      return false;
    }
  }

  /**
   * Set value with expiration (alias for convenience)
   */
  async setex(key, ttl, value) {
    return this.set(key, value, ttl);
  }

  /**
   * Delete key from cache
   */
  async del(key) {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await this.client.del(key);
      this.stats.deletes++;
      logger.debug(`🗑️ Cache DELETE for key: ${key}`);
      return result > 0;
    } catch (error) {
      logger.error('Cache delete error:', error);
      this.stats.errors++;
      return false;
    }
  }

  /**
   * Check if key exists
   */
  async exists(key) {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      logger.error('Cache exists error:', error);
      this.stats.errors++;
      return false;
    }
  }

  /**
   * Increment counter
   */
  async incr(key) {
    if (!this.isConnected) {
      return 0;
    }

    try {
      return await this.client.incr(key);
    } catch (error) {
      logger.error('Cache incr error:', error);
      this.stats.errors++;
      return 0;
    }
  }

  /**
   * Set expiration for existing key
   */
  async expire(key, ttl) {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await this.client.expire(key, ttl);
      return result === 1;
    } catch (error) {
      logger.error('Cache expire error:', error);
      this.stats.errors++;
      return false;
    }
  }

  /**
   * Get multiple keys at once
   */
  async mget(keys) {
    if (!this.isConnected || !keys.length) {
      return {};
    }

    try {
      const values = await this.client.mGet(keys);
      const result = {};
      
      keys.forEach((key, index) => {
        if (values[index] !== null) {
          try {
            result[key] = JSON.parse(values[index]);
            this.stats.hits++;
          } catch (error) {
            logger.error(`Failed to parse cached value for key ${key}:`, error);
            this.stats.misses++;
          }
        } else {
          this.stats.misses++;
        }
      });

      return result;
    } catch (error) {
      logger.error('Cache mget error:', error);
      this.stats.errors++;
      return {};
    }
  }

  /**
   * Cache document parsing result with intelligent key generation
   * PROMPT 2: Avoid re-parsing identical documents
   */
  async cacheParsingResult(file, result, ttl = 3600) {
    try {
      // Generate content-based cache key
      const contentHash = this.generateContentHash(file);
      const metadataHash = this.generateMetadataHash(file);
      
      // Store with multiple keys for different lookup strategies
      const keys = [
        `cv:content:${contentHash}`,
        `cv:metadata:${metadataHash}`,
        `cv:combined:${contentHash}:${metadataHash}`
      ];

      // Store the result with all keys
      const promises = keys.map(key => this.set(key, {
        ...result,
        cached_at: new Date().toISOString(),
        cache_key: contentHash,
        original_filename: file.originalname
      }, ttl));

      await Promise.all(promises);

      // Store reverse lookup for cache invalidation
      await this.set(`lookup:${contentHash}`, keys, ttl);

      logger.info(`📦 Cached parsing result with ${keys.length} keys`, {
        contentHash: contentHash.substring(0, 12),
        filename: file.originalname,
        size: file.size
      });

      return contentHash;
    } catch (error) {
      logger.error('Failed to cache parsing result:', error);
      return null;
    }
  }

  /**
   * Find cached parsing result for similar document
   * PROMPT 2: Intelligent duplicate detection
   */
  async findCachedResult(file) {
    try {
      const contentHash = this.generateContentHash(file);
      const metadataHash = this.generateMetadataHash(file);

      // Try different lookup strategies
      const lookupKeys = [
        `cv:content:${contentHash}`,        // Exact content match
        `cv:metadata:${metadataHash}`,      // Similar metadata
        `cv:combined:${contentHash}:${metadataHash}` // Combined match
      ];

      // Check for exact matches first
      for (const key of lookupKeys) {
        const result = await this.get(key);
        if (result) {
          logger.info(`🎯 Found cached result for ${file.originalname}`, {
            cacheKey: key,
            cachedAt: result.cached_at
          });
          return result;
        }
      }

      // Try fuzzy matching for similar files
      const similarResult = await this.findSimilarDocument(file, contentHash);
      if (similarResult) {
        return similarResult;
      }

      return null;
    } catch (error) {
      logger.error('Failed to find cached result:', error);
      return null;
    }
  }

  /**
   * Find similar documents using fuzzy matching
   */
  async findSimilarDocument(file, contentHash) {
    try {
      // Look for files with similar names and sizes
      const pattern = `cv:metadata:*`;
      const keys = await this.client.keys(pattern);
      
      for (const key of keys.slice(0, 50)) { // Limit to prevent performance issues
        const cached = await this.get(key);
        if (cached && this.isSimilarDocument(file, cached)) {
          logger.info(`🔍 Found similar cached document for ${file.originalname}`);
          return cached;
        }
      }

      return null;
    } catch (error) {
      logger.error('Failed to find similar document:', error);
      return null;
    }
  }

  /**
   * Check if two documents are similar
   */
  isSimilarDocument(file, cachedResult) {
    if (!cachedResult.original_filename) {
      return false;
    }

    // Check file size similarity (within 10%)
    const sizeDiff = Math.abs(file.size - (cachedResult.original_size || 0));
    const sizeThreshold = file.size * 0.1;
    
    if (sizeDiff > sizeThreshold) {
      return false;
    }

    // Check filename similarity
    const similarity = this.calculateStringSimilarity(
      file.originalname.toLowerCase(),
      cachedResult.original_filename.toLowerCase()
    );

    return similarity > 0.8; // 80% similarity threshold
  }

  /**
   * Calculate string similarity using Levenshtein distance
   */
  calculateStringSimilarity(str1, str2) {
    const matrix = [];
    const len1 = str1.length;
    const len2 = str2.length;

    // Create matrix
    for (let i = 0; i <= len2; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= len1; j++) {
      matrix[0][j] = j;
    }

    // Fill matrix
    for (let i = 1; i <= len2; i++) {
      for (let j = 1; j <= len1; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }

    const maxLen = Math.max(len1, len2);
    return (maxLen - matrix[len2][len1]) / maxLen;
  }

  /**
   * Generate content-based hash for file
   */
  generateContentHash(file) {
    const hash = crypto.createHash('sha256');
    hash.update(file.buffer);
    return hash.digest('hex');
  }

  /**
   * Generate metadata-based hash for file
   */
  generateMetadataHash(file) {
    const hash = crypto.createHash('md5');
    hash.update(file.originalname);
    hash.update(file.size.toString());
    hash.update(file.mimetype);
    return hash.digest('hex');
  }

  /**
   * Cache user session data
   */
  async cacheUserSession(userId, sessionData, ttl = 86400) {
    return this.set(`session:${userId}`, sessionData, ttl);
  }

  /**
   * Get user session data
   */
  async getUserSession(userId) {
    return this.get(`session:${userId}`);
  }

  /**
   * Cache task progress
   */
  async cacheTaskProgress(taskId, progress, ttl = 1800) {
    return this.set(`task:${taskId}:progress`, progress, ttl);
  }

  /**
   * Get task progress
   */
  async getTaskProgress(taskId) {
    return this.get(`task:${taskId}:progress`);
  }

  /**
   * Invalidate cache by pattern
   */
  async invalidatePattern(pattern) {
    try {
      const keys = await this.client.keys(pattern);
      if (keys.length > 0) {
        await this.client.del(keys);
        logger.info(`🗑️ Invalidated ${keys.length} cache keys matching pattern: ${pattern}`);
      }
      return keys.length;
    } catch (error) {
      logger.error('Failed to invalidate cache pattern:', error);
      return 0;
    }
  }

  /**
   * Get cache statistics
   * PROMPT 2: Monitor 85%+ hit ratio target
   */
  getStats() {
    const total = this.stats.hits + this.stats.misses;
    const hitRatio = total > 0 ? this.stats.hits / total : 0;

    return {
      ...this.stats,
      totalRequests: total,
      hitRatio: Math.round(hitRatio * 10000) / 100, // Percentage with 2 decimals
      isConnected: this.isConnected,
      target: {
        hitRatio: 85,
        status: hitRatio >= 0.85 ? 'ACHIEVED' : 'BELOW_TARGET'
      }
    };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      errors: 0
    };
    logger.info('📊 Cache statistics reset');
  }

  /**
   * Health check for cache service
   */
  async healthCheck() {
    try {
      if (!this.isConnected) {
        return { status: 'DOWN', error: 'Not connected to Redis' };
      }

      const start = Date.now();
      await this.client.ping();
      const latency = Date.now() - start;

      return {
        status: 'UP',
        latency: `${latency}ms`,
        stats: this.getStats()
      };
    } catch (error) {
      return {
        status: 'DOWN',
        error: error.message
      };
    }
  }
}

module.exports = CacheService;
