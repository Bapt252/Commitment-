/**
 * CV Routes - API endpoints for CV Parser Ultra v2.0
 * PROMPT 2: REST API with streaming support
 */

const express = require('express');
const multer = require('multer');
const crypto = require('crypto');
const path = require('path');

const uploadMiddleware = require('../middleware/uploadMiddleware');
const { validateCVUpload } = require('../middleware/validationMiddleware');
const logger = require('../utils/logger');

function createCVRoutes(services) {
  const router = express.Router();
  const { parsing, cache, validation, metrics, websocket } = services;

  /**
   * POST /api/v2/parse/cv/stream
   * PROMPT 2: Parse CV with real-time streaming
   */
  router.post('/stream', uploadMiddleware.single('cv'), validateCVUpload, async (req, res) => {
    const taskId = crypto.randomUUID();
    const startTime = Date.now();

    try {
      logger.info(`🚀 Starting CV parsing stream for task ${taskId}`, {
        filename: req.file.originalname,
        size: req.file.size,
        mimetype: req.file.mimetype,
        userId: req.user?.id
      });

      // Immediate response with task ID
      res.status(202).json({
        taskId,
        status: 'processing',
        message: 'CV parsing started. Connect to WebSocket for real-time updates.',
        websocket: `/api/v2/parse/status/${taskId}`,
        timestamp: new Date().toISOString()
      });

      // Start parsing with WebSocket progress updates
      const progressCallback = (progress) => {
        // Send to specific task room via WebSocket service
        websocket.sendToTask(taskId, 'parsing_progress', progress);
      };

      // Process asynchronously
      setImmediate(async () => {
        try {
          const result = await parsing.parseCV(req.file, {
            taskId,
            progressCallback,
            userId: req.user?.id
          });

          // Cache the result
          await cache.setex(`task:${taskId}`, 3600, result);

          // Record metrics
          const duration = Date.now() - startTime;
          metrics.recordParsingOperation({
            duration,
            fileType: req.file.mimetype,
            cacheHit: false,
            success: true
          });

          // Send completion via WebSocket
          websocket.sendToTask(taskId, 'parsing_completed', {
            taskId,
            data: result.data,
            duration,
            confidence: result.data.confidence
          });

        } catch (error) {
          logger.error(`❌ Async parsing failed for task ${taskId}:`, error);
          
          // Send error via WebSocket
          websocket.sendToTask(taskId, 'parsing_error', {
            taskId,
            error: error.message,
            fallback_required: true
          });
        }
      });

    } catch (error) {
      logger.error(`❌ CV parsing stream failed for task ${taskId}:`, error);
      
      const duration = Date.now() - startTime;
      metrics.recordParsingOperation({
        duration,
        fileType: req.file?.mimetype || 'unknown',
        success: false
      });

      res.status(500).json({
        error: 'Parsing failed',
        message: error.message,
        taskId,
        fallback_available: true
      });
    }
  });

  /**
   * GET /api/v2/parse/status/:taskId
   * PROMPT 2: Get task status and results
   */
  router.get('/status/:taskId', async (req, res) => {
    const { taskId } = req.params;

    try {
      // Check active tasks first
      const activeTask = websocket.activeTasks?.get(taskId);
      
      if (activeTask) {
        return res.json({
          taskId,
          status: activeTask.status,
          startTime: activeTask.startTime,
          result: activeTask.result || null
        });
      }

      // Check cache for completed tasks
      const cachedResult = await cache.get(`task:${taskId}`);
      
      if (cachedResult) {
        return res.json({
          taskId,
          status: 'completed',
          result: cachedResult,
          fromCache: true
        });
      }

      // Task not found
      res.status(404).json({
        error: 'Task not found',
        taskId,
        message: 'Task may have expired or never existed'
      });

    } catch (error) {
      logger.error(`Error getting task status for ${taskId}:`, error);
      res.status(500).json({
        error: 'Failed to get task status',
        taskId
      });
    }
  });

  /**
   * POST /api/v2/parse/cv/upload
   * PROMPT 2: Traditional upload without streaming (for compatibility)
   */
  router.post('/upload', uploadMiddleware.single('cv'), validateCVUpload, async (req, res) => {
    const taskId = crypto.randomUUID();
    const startTime = Date.now();

    try {
      logger.info(`📄 Traditional CV upload for task ${taskId}`, {
        filename: req.file.originalname,
        size: req.file.size
      });

      // Check cache first
      const cacheKey = await parsing.generateCacheKey(req.file);
      const cached = await cache.get(`cv:${cacheKey}`);
      
      if (cached) {
        metrics.recordParsingOperation({
          duration: Date.now() - startTime,
          fileType: req.file.mimetype,
          cacheHit: true,
          success: true
        });

        return res.json({
          taskId,
          status: 'completed',
          data: cached,
          fromCache: true,
          duration: Date.now() - startTime
        });
      }

      // Parse without streaming
      const result = await parsing.parseCV(req.file, { taskId });

      const duration = Date.now() - startTime;
      metrics.recordParsingOperation({
        duration,
        fileType: req.file.mimetype,
        cacheHit: false,
        success: true
      });

      res.json({
        taskId,
        status: 'completed',
        data: result.data,
        duration,
        confidence: result.data.confidence
      });

    } catch (error) {
      logger.error(`❌ Traditional CV upload failed for task ${taskId}:`, error);
      
      metrics.recordParsingOperation({
        duration: Date.now() - startTime,
        fileType: req.file?.mimetype || 'unknown',
        success: false
      });

      res.status(500).json({
        error: 'Parsing failed',
        message: error.message,
        taskId,
        fallback_available: true
      });
    }
  });

  /**
   * GET /api/v2/parse/cv/:taskId/download
   * PROMPT 2: Download processed CV data as JSON
   */
  router.get('/:taskId/download', async (req, res) => {
    const { taskId } = req.params;
    const { format = 'json' } = req.query;

    try {
      const result = await cache.get(`task:${taskId}`) || 
                    await cache.get(`task:${taskId}:validated`);

      if (!result) {
        return res.status(404).json({
          error: 'Task results not found',
          taskId
        });
      }

      const filename = `cv_${taskId}.${format}`;

      switch (format) {
        case 'json':
          res.setHeader('Content-Type', 'application/json');
          res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
          res.json(result.data);
          break;

        case 'csv':
          // Convert to CSV format
          const csv = convertToCSV(result.data);
          res.setHeader('Content-Type', 'text/csv');
          res.setHeader('Content-Disposition', `attachment; filename="cv_${taskId}.csv"`);
          res.send(csv);
          break;

        default:
          res.status(400).json({
            error: 'Unsupported format',
            supportedFormats: ['json', 'csv']
          });
      }

    } catch (error) {
      logger.error(`Error downloading CV data for ${taskId}:`, error);
      res.status(500).json({
        error: 'Failed to download CV data',
        taskId
      });
    }
  });

  /**
   * DELETE /api/v2/parse/cv/:taskId
   * PROMPT 2: Delete task and its cached data
   */
  router.delete('/:taskId', async (req, res) => {
    const { taskId } = req.params;

    try {
      // Delete from cache
      const deleted = await Promise.all([
        cache.del(`task:${taskId}`),
        cache.del(`task:${taskId}:validated`),
        cache.del(`task:${taskId}:corrected`),
        cache.del(`task:${taskId}:progress`)
      ]);

      // Remove from active tasks
      if (websocket.activeTasks?.has(taskId)) {
        websocket.activeTasks.delete(taskId);
      }

      logger.info(`🗑️ Deleted task ${taskId}`, {
        cacheEntriesDeleted: deleted.filter(Boolean).length
      });

      res.json({
        taskId,
        deleted: true,
        message: 'Task and associated data deleted successfully'
      });

    } catch (error) {
      logger.error(`Error deleting task ${taskId}:`, error);
      res.status(500).json({
        error: 'Failed to delete task',
        taskId
      });
    }
  });

  /**
   * GET /api/v2/parse/cv/stats
   * PROMPT 2: Get parsing service statistics
   */
  router.get('/stats', async (req, res) => {
    try {
      const stats = {
        parsing: parsing.getStats(),
        cache: cache.getStats(),
        websocket: websocket.getStats(),
        validation: validation.getStats(),
        metrics: await metrics.getMetricsSummary()
      };

      res.json({
        service: 'CV Parser Ultra v2.0',
        version: '2.0.0',
        timestamp: new Date().toISOString(),
        stats
      });

    } catch (error) {
      logger.error('Error getting CV parser stats:', error);
      res.status(500).json({
        error: 'Failed to get statistics'
      });
    }
  });

  /**
   * Helper function to convert CV data to CSV
   */
  function convertToCSV(data) {
    const rows = [];
    
    // Personal information
    if (data.personal) {
      rows.push(['Section', 'Field', 'Value']);
      Object.entries(data.personal).forEach(([key, value]) => {
        rows.push(['Personal', key, value || '']);
      });
    }

    // Skills
    if (data.skills) {
      if (data.skills.technical) {
        data.skills.technical.forEach(skill => {
          rows.push(['Skills', 'Technical', skill]);
        });
      }
      if (data.skills.soft) {
        data.skills.soft.forEach(skill => {
          rows.push(['Skills', 'Soft', skill]);
        });
      }
    }

    // Experience
    if (data.experience) {
      data.experience.forEach((exp, index) => {
        rows.push(['Experience', `Position ${index + 1}`, exp.position || '']);
        rows.push(['Experience', `Company ${index + 1}`, exp.company || '']);
        rows.push(['Experience', `Duration ${index + 1}`, `${exp.startDate} - ${exp.endDate}`]);
      });
    }

    // Convert to CSV string
    return rows.map(row => 
      row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ).join('\n');
  }

  return router;
}

module.exports = createCVRoutes;
