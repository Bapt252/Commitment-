/**
 * WebSocket Service - Real-time streaming for CV parsing
 * PROMPT 2: <500ms first response, real-time progress updates
 */

const logger = require('../utils/logger');

class WebSocketService {
  constructor(io, services) {
    this.io = io;
    this.services = services;
    this.activeTasks = new Map();
    this.connections = new Map();
    
    this.setupEventHandlers();
    
    logger.info('🔌 WebSocket service initialized for real-time streaming');
  }

  setupEventHandlers() {
    this.io.on('connection', (socket) => {
      logger.info(`🔗 Client connected: ${socket.id}`);
      this.connections.set(socket.id, {
        connectedAt: new Date(),
        lastActivity: new Date()
      });

      // Update metrics
      this.services.metrics.recordWebSocketConnection();

      // Authentication for WebSocket (if needed)
      socket.on('authenticate', async (data) => {
        try {
          // Validate JWT token if provided
          if (data.token) {
            // JWT validation logic here
            socket.authenticated = true;
            socket.userId = data.userId;
            logger.info(`🔐 Socket ${socket.id} authenticated for user ${data.userId}`);
          }
        } catch (error) {
          logger.error('WebSocket authentication failed:', error);
          socket.emit('auth_error', { message: 'Authentication failed' });
        }
      });

      // Handle CV parsing requests via WebSocket
      socket.on('parse_cv', async (data) => {
        try {
          await this.handleCVParsing(socket, data);
        } catch (error) {
          logger.error('WebSocket CV parsing error:', error);
          socket.emit('parsing_error', {
            taskId: data.taskId,
            error: error.message
          });
        }
      });

      // Handle task status requests
      socket.on('get_task_status', async (data) => {
        try {
          await this.handleTaskStatus(socket, data);
        } catch (error) {
          logger.error('WebSocket task status error:', error);
          socket.emit('status_error', {
            taskId: data.taskId,
            error: error.message
          });
        }
      });

      // Handle validation interactions
      socket.on('submit_validation', async (data) => {
        try {
          await this.handleValidationSubmission(socket, data);
        } catch (error) {
          logger.error('WebSocket validation error:', error);
          socket.emit('validation_error', {
            taskId: data.taskId,
            error: error.message
          });
        }
      });

      // Handle corrections submission
      socket.on('submit_corrections', async (data) => {
        try {
          await this.handleCorrections(socket, data);
        } catch (error) {
          logger.error('WebSocket corrections error:', error);
          socket.emit('corrections_error', {
            taskId: data.taskId,
            error: error.message
          });
        }
      });

      // Handle real-time chat for manual fallback
      socket.on('manual_fallback_request', async (data) => {
        try {
          await this.handleManualFallback(socket, data);
        } catch (error) {
          logger.error('WebSocket manual fallback error:', error);
          socket.emit('fallback_error', {
            taskId: data.taskId,
            error: error.message
          });
        }
      });

      // Handle disconnection
      socket.on('disconnect', (reason) => {
        logger.info(`🔌 Client disconnected: ${socket.id}, reason: ${reason}`);
        
        // Clean up active tasks for this socket
        this.cleanupSocketTasks(socket.id);
        
        // Remove from connections
        this.connections.delete(socket.id);
        
        // Update metrics
        this.services.metrics.recordWebSocketDisconnection();
      });

      // Handle ping/pong for connection health
      socket.on('ping', () => {
        const connection = this.connections.get(socket.id);
        if (connection) {
          connection.lastActivity = new Date();
        }
        socket.emit('pong', { timestamp: Date.now() });
      });

      // Send welcome message with capabilities
      socket.emit('connected', {
        socketId: socket.id,
        timestamp: new Date().toISOString(),
        capabilities: [
          'real_time_parsing',
          'progress_tracking', 
          'interactive_validation',
          'manual_corrections',
          'fallback_support'
        ],
        version: '2.0.0'
      });
    });
  }

  /**
   * Handle CV parsing with real-time progress
   * PROMPT 2: Stream progress updates via WebSocket
   */
  async handleCVParsing(socket, data) {
    const { taskId, fileBuffer, fileName, fileType } = data;
    
    if (!fileBuffer || !fileName) {
      throw new Error('Missing required file data');
    }

    logger.info(`📄 Starting WebSocket CV parsing for task ${taskId}`);

    // Track active task
    this.activeTasks.set(taskId, {
      socketId: socket.id,
      startTime: Date.now(),
      status: 'processing'
    });

    // Create file object for parsing service
    const file = {
      buffer: Buffer.from(fileBuffer, 'base64'),
      originalname: fileName,
      mimetype: fileType,
      size: Buffer.byteLength(fileBuffer, 'base64')
    };

    // Real-time progress callback
    const progressCallback = (progress) => {
      socket.emit('parsing_progress', progress);
      
      // Also emit to parsing status room for any listeners
      socket.to(`task:${taskId}`).emit('parsing_progress', progress);
      
      logger.debug(`📊 Progress update for ${taskId}: ${progress.progress}% - ${progress.stage}`);
    };

    try {
      // Start parsing with real-time callbacks
      const result = await this.services.parsing.parseCV(file, {
        taskId,
        progressCallback
      });

      // Update task status
      this.activeTasks.set(taskId, {
        ...this.activeTasks.get(taskId),
        status: 'completed',
        result
      });

      // Send completion notification
      socket.emit('parsing_completed', {
        taskId,
        data: result.data,
        duration: result.duration,
        timestamp: new Date().toISOString()
      });

      logger.info(`✅ WebSocket CV parsing completed for task ${taskId}`);

    } catch (error) {
      // Update task status
      this.activeTasks.set(taskId, {
        ...this.activeTasks.get(taskId),
        status: 'error',
        error: error.message
      });

      throw error;
    }
  }

  /**
   * Handle task status requests
   * PROMPT 2: Real-time status tracking
   */
  async handleTaskStatus(socket, data) {
    const { taskId } = data;
    
    // Join task-specific room for real-time updates
    socket.join(`task:${taskId}`);
    
    // Get current task status
    const activeTask = this.activeTasks.get(taskId);
    
    if (activeTask) {
      socket.emit('task_status', {
        taskId,
        status: activeTask.status,
        startTime: activeTask.startTime,
        socketId: activeTask.socketId,
        result: activeTask.result || null,
        error: activeTask.error || null
      });
    } else {
      // Check cache for completed tasks
      const cachedResult = await this.services.cache.get(`task:${taskId}`);
      
      if (cachedResult) {
        socket.emit('task_status', {
          taskId,
          status: 'completed',
          result: cachedResult,
          fromCache: true
        });
      } else {
        socket.emit('task_status', {
          taskId,
          status: 'not_found',
          message: 'Task not found or expired'
        });
      }
    }
  }

  /**
   * Handle interactive validation
   * PROMPT 2: User can validate and correct extracted data
   */
  async handleValidationSubmission(socket, data) {
    const { taskId, validatedFields, corrections } = data;
    
    logger.info(`📝 Processing validation for task ${taskId}`);

    try {
      // Process validation with the validation service
      const validationResult = await this.services.validation.processValidation({
        taskId,
        validatedFields,
        corrections,
        userId: socket.userId
      });

      // Update cached result with validated data
      await this.services.cache.setex(`task:${taskId}:validated`, 3600, validationResult);

      // Emit validation confirmation
      socket.emit('validation_processed', {
        taskId,
        validatedData: validationResult,
        timestamp: new Date().toISOString()
      });

      // Notify other listeners in the task room
      socket.to(`task:${taskId}`).emit('validation_updated', {
        taskId,
        updatedBy: socket.userId,
        timestamp: new Date().toISOString()
      });

      logger.info(`✅ Validation processed for task ${taskId}`);

    } catch (error) {
      logger.error(`❌ Validation failed for task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Handle user corrections
   * PROMPT 2: Allow manual corrections with real-time updates
   */
  async handleCorrections(socket, data) {
    const { taskId, corrections, field } = data;
    
    logger.info(`🔧 Processing corrections for task ${taskId}, field: ${field}`);

    try {
      // Apply corrections
      const correctedResult = await this.services.validation.applyCorrections({
        taskId,
        corrections,
        field,
        userId: socket.userId
      });

      // Update cache with corrected data
      await this.services.cache.setex(`task:${taskId}:corrected`, 3600, correctedResult);

      // Emit corrections confirmation
      socket.emit('corrections_applied', {
        taskId,
        field,
        correctedData: correctedResult,
        timestamp: new Date().toISOString()
      });

      // Real-time notification to other listeners
      socket.to(`task:${taskId}`).emit('corrections_updated', {
        taskId,
        field,
        updatedBy: socket.userId,
        timestamp: new Date().toISOString()
      });

      logger.info(`✅ Corrections applied for task ${taskId}`);

    } catch (error) {
      logger.error(`❌ Corrections failed for task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Handle manual fallback requests
   * PROMPT 2: Smooth transition to manual input when AI fails
   */
  async handleManualFallback(socket, data) {
    const { taskId, reason } = data;
    
    logger.info(`🆘 Manual fallback requested for task ${taskId}, reason: ${reason}`);

    try {
      // Create manual fallback session
      const fallbackSession = {
        taskId,
        socketId: socket.id,
        userId: socket.userId,
        reason,
        startTime: Date.now(),
        status: 'active'
      };

      // Store fallback session
      await this.services.cache.setex(`fallback:${taskId}`, 1800, fallbackSession); // 30 min

      // Join fallback room for assistance
      socket.join(`fallback:${taskId}`);

      // Emit fallback session start
      socket.emit('fallback_session_started', {
        taskId,
        sessionId: `fallback:${taskId}`,
        message: 'Manual fallback session started. You can now input data manually.',
        template: this.getManualInputTemplate(),
        timestamp: new Date().toISOString()
      });

      // Notify support team if available
      socket.to('support_team').emit('fallback_request', {
        taskId,
        userId: socket.userId,
        reason,
        timestamp: new Date().toISOString()
      });

      logger.info(`✅ Manual fallback session started for task ${taskId}`);

    } catch (error) {
      logger.error(`❌ Manual fallback failed for task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Get manual input template for fallback
   */
  getManualInputTemplate() {
    return {
      personal: {
        firstName: '',
        lastName: '',
        title: '',
        email: '',
        phone: '',
        address: ''
      },
      skills: {
        technical: [],
        soft: [],
        software: []
      },
      languages: [],
      certifications: [],
      experience: [],
      education: []
    };
  }

  /**
   * Clean up tasks for disconnected socket
   */
  cleanupSocketTasks(socketId) {
    for (const [taskId, task] of this.activeTasks.entries()) {
      if (task.socketId === socketId) {
        logger.info(`🧹 Cleaning up abandoned task ${taskId} for socket ${socketId}`);
        this.activeTasks.delete(taskId);
      }
    }
  }

  /**
   * Get WebSocket service statistics
   */
  getStats() {
    return {
      activeConnections: this.connections.size,
      activeTasks: this.activeTasks.size,
      connectionDetails: Array.from(this.connections.entries()).map(([id, conn]) => ({
        socketId: id,
        connectedAt: conn.connectedAt,
        lastActivity: conn.lastActivity
      })),
      activeTasksList: Array.from(this.activeTasks.entries()).map(([taskId, task]) => ({
        taskId,
        status: task.status,
        startTime: task.startTime,
        socketId: task.socketId
      }))
    };
  }

  /**
   * Send message to specific task room
   */
  sendToTask(taskId, event, data) {
    this.io.to(`task:${taskId}`).emit(event, data);
  }

  /**
   * Send message to all connected clients
   */
  broadcast(event, data) {
    this.io.emit(event, data);
  }

  /**
   * Send message to specific socket
   */
  sendToSocket(socketId, event, data) {
    this.io.to(socketId).emit(event, data);
  }
}

module.exports = WebSocketService;
