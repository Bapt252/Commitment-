/**
 * Validation Routes - Interactive validation and corrections
 * PROMPT 2: User validation and manual corrections API
 */

const express = require('express');
const { body, param, validationResult } = require('express-validator');
const logger = require('../utils/logger');

function createValidationRoutes(services) {
  const router = express.Router();
  const { validation, cache, websocket, metrics } = services;

  /**
   * GET /api/v2/parse/validate/:taskId
   * PROMPT 2: Get validation interface for extracted data
   */
  router.get('/:taskId', 
    param('taskId').isUUID().withMessage('Invalid task ID'),
    async (req, res) => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { taskId } = req.params;

      try {
        // Get parsed data
        const taskData = await cache.get(`task:${taskId}`) ||
                         await cache.get(`task:${taskId}:validated`);

        if (!taskData) {
          return res.status(404).json({
            error: 'Task not found',
            taskId,
            message: 'Task may have expired or validation already completed'
          });
        }

        // Validate the current data
        const validationResult = await validation.validateCVData(taskData.data);

        // Generate smart suggestions
        const suggestions = validation.generateSmartSuggestions(taskData.data, validationResult);

        res.json({
          taskId,
          data: taskData.data,
          validation: validationResult,
          suggestions,
          confidence: taskData.confidence || 0,
          validationInterface: {
            sections: [
              {
                name: 'personal',
                label: 'Informations Personnelles',
                fields: [
                  { key: 'firstName', label: 'Prénom', type: 'text', required: true },
                  { key: 'lastName', label: 'Nom', type: 'text', required: true },
                  { key: 'title', label: 'Titre professionnel', type: 'text' },
                  { key: 'email', label: 'Email', type: 'email', required: true },
                  { key: 'phone', label: 'Téléphone', type: 'tel' },
                  { key: 'address', label: 'Adresse', type: 'textarea' }
                ]
              },
              {
                name: 'skills',
                label: 'Compétences',
                fields: [
                  { key: 'technical', label: 'Compétences techniques', type: 'array' },
                  { key: 'soft', label: 'Compétences relationnelles', type: 'array' },
                  { key: 'software', label: 'Logiciels', type: 'object_array' }
                ]
              },
              {
                name: 'experience',
                label: 'Expérience Professionnelle',
                type: 'dynamic_array',
                fields: [
                  { key: 'position', label: 'Poste', type: 'text', required: true },
                  { key: 'company', label: 'Entreprise', type: 'text', required: true },
                  { key: 'location', label: 'Lieu', type: 'text' },
                  { key: 'startDate', label: 'Date de début', type: 'month', required: true },
                  { key: 'endDate', label: 'Date de fin', type: 'month_or_current', required: true },
                  { key: 'description', label: 'Description', type: 'textarea' },
                  { key: 'technologies', label: 'Technologies utilisées', type: 'array' }
                ]
              },
              {
                name: 'education',
                label: 'Formation',
                type: 'dynamic_array',
                fields: [
                  { key: 'degree', label: 'Diplôme', type: 'text', required: true },
                  { key: 'institution', label: 'Établissement', type: 'text', required: true },
                  { key: 'location', label: 'Lieu', type: 'text' },
                  { key: 'graduationDate', label: 'Date d\'obtention', type: 'month' },
                  { key: 'grade', label: 'Mention', type: 'text' }
                ]
              },
              {
                name: 'languages',
                label: 'Langues',
                type: 'dynamic_array',
                fields: [
                  { key: 'language', label: 'Langue', type: 'text', required: true },
                  { key: 'level', label: 'Niveau', type: 'select', options: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'natif'], required: true }
                ]
              },
              {
                name: 'certifications',
                label: 'Certifications',
                type: 'array',
                fields: [
                  { key: 'certification', label: 'Certification', type: 'text' }
                ]
              }
            ]
          },
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        logger.error(`Error getting validation data for ${taskId}:`, error);
        res.status(500).json({
          error: 'Failed to get validation data',
          taskId
        });
      }
    }
  );

  /**
   * PUT /api/v2/parse/validate/:taskId
   * PROMPT 2: Submit user validation and corrections
   */
  router.put('/:taskId',
    param('taskId').isUUID().withMessage('Invalid task ID'),
    body('validatedFields').optional().isObject().withMessage('Validated fields must be an object'),
    body('corrections').optional().isObject().withMessage('Corrections must be an object'),
    body('userFeedback').optional().isObject().withMessage('User feedback must be an object'),
    async (req, res) => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { taskId } = req.params;
      const { validatedFields, corrections, userFeedback } = req.body;
      const userId = req.user?.id;

      try {
        logger.info(`📝 Processing validation submission for task ${taskId}`, {
          userId,
          hasValidatedFields: !!validatedFields,
          hasCorrections: !!corrections,
          hasFeedback: !!userFeedback
        });

        // Process the validation
        const result = await validation.processValidation({
          taskId,
          validatedFields,
          corrections,
          userId
        });

        // Record metrics
        metrics.recordValidationEvent('validation_submitted', 'general');
        if (corrections) {
          metrics.recordCorrections(Object.keys(corrections).length, 'user');
        }
        if (result.userValidation?.satisfactionScore) {
          metrics.recordUserSatisfaction(result.userValidation.satisfactionScore);
        }

        // Send real-time update via WebSocket
        websocket.sendToTask(taskId, 'validation_completed', {
          taskId,
          validatedData: result.data,
          confidence: result.confidence,
          satisfactionScore: result.userValidation?.satisfactionScore
        });

        res.json({
          taskId,
          status: 'validated',
          data: result.data,
          validation: result.validation,
          userValidation: result.userValidation,
          confidence: result.confidence,
          message: 'Validation processed successfully',
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        logger.error(`❌ Validation submission failed for task ${taskId}:`, error);
        res.status(500).json({
          error: 'Validation processing failed',
          message: error.message,
          taskId
        });
      }
    }
  );

  /**
   * PUT /api/v2/parse/corrections/:taskId/:field
   * PROMPT 2: Apply specific field corrections
   */
  router.put('/corrections/:taskId/:field',
    param('taskId').isUUID().withMessage('Invalid task ID'),
    param('field').isString().withMessage('Field name is required'),
    body('corrections').isObject().withMessage('Corrections are required'),
    async (req, res) => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { taskId, field } = req.params;
      const { corrections } = req.body;
      const userId = req.user?.id;

      try {
        logger.info(`🔧 Applying field corrections for task ${taskId}`, {
          field,
          userId,
          correctionsKeys: Object.keys(corrections)
        });

        // Apply corrections
        const result = await validation.applyCorrections({
          taskId,
          corrections,
          field,
          userId
        });

        // Record metrics
        metrics.recordValidationEvent('field_corrected', field);
        metrics.recordCorrections(1, 'field_specific');

        // Send real-time update via WebSocket
        websocket.sendToTask(taskId, 'field_corrected', {
          taskId,
          field,
          correctedData: result.data,
          timestamp: new Date().toISOString()
        });

        res.json({
          taskId,
          field,
          status: 'corrected',
          data: result.data,
          validation: result.validation,
          message: `Field ${field} corrected successfully`,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        logger.error(`❌ Field correction failed for task ${taskId}, field ${field}:`, error);
        res.status(500).json({
          error: 'Field correction failed',
          message: error.message,
          taskId,
          field
        });
      }
    }
  );

  /**
   * POST /api/v2/parse/validate/:taskId/feedback
   * PROMPT 2: Submit user satisfaction feedback
   */
  router.post('/:taskId/feedback',
    param('taskId').isUUID().withMessage('Invalid task ID'),
    body('satisfactionScore').isInt({ min: 1, max: 5 }).withMessage('Satisfaction score must be between 1 and 5'),
    body('feedback').optional().isString().withMessage('Feedback must be a string'),
    body('improvementSuggestions').optional().isArray().withMessage('Improvement suggestions must be an array'),
    async (req, res) => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { taskId } = req.params;
      const { satisfactionScore, feedback, improvementSuggestions } = req.body;
      const userId = req.user?.id;

      try {
        // Store feedback
        const feedbackData = {
          taskId,
          userId,
          satisfactionScore,
          feedback,
          improvementSuggestions,
          timestamp: new Date().toISOString()
        };

        await cache.setex(`feedback:${taskId}`, 86400, feedbackData); // 24 hours

        // Convert 1-5 scale to 0-100 for metrics
        const normalizedScore = ((satisfactionScore - 1) / 4) * 100;
        metrics.recordUserSatisfaction(normalizedScore, 'feedback');

        // Record feedback event
        metrics.recordValidationEvent('feedback_submitted', 'user_satisfaction');

        logger.info(`💬 User feedback received for task ${taskId}`, {
          userId,
          satisfactionScore,
          hasTextFeedback: !!feedback,
          hasSuggestions: !!improvementSuggestions
        });

        res.json({
          taskId,
          message: 'Feedback received successfully',
          satisfactionScore,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        logger.error(`Error storing feedback for task ${taskId}:`, error);
        res.status(500).json({
          error: 'Failed to store feedback',
          taskId
        });
      }
    }
  );

  /**
   * POST /api/v2/parse/validate/:taskId/manual-fallback
   * PROMPT 2: Initiate manual fallback session
   */
  router.post('/:taskId/manual-fallback',
    param('taskId').isUUID().withMessage('Invalid task ID'),
    body('reason').isString().withMessage('Reason for fallback is required'),
    body('section').optional().isString().withMessage('Section must be a string'),
    async (req, res) => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const { taskId } = req.params;
      const { reason, section } = req.body;
      const userId = req.user?.id;

      try {
        logger.info(`🆘 Manual fallback requested for task ${taskId}`, {
          userId,
          reason,
          section
        });

        // Create fallback session
        const fallbackSession = {
          taskId,
          userId,
          reason,
          section,
          status: 'active',
          startTime: new Date().toISOString(),
          template: validation.getManualInputTemplate ? 
            validation.getManualInputTemplate() : 
            getDefaultTemplate()
        };

        await cache.setex(`fallback:${taskId}`, 1800, fallbackSession); // 30 minutes

        // Record metrics
        metrics.recordValidationEvent('manual_fallback_requested', section || 'general');

        // Notify via WebSocket
        websocket.sendToTask(taskId, 'fallback_session_started', {
          taskId,
          sessionId: `fallback:${taskId}`,
          template: fallbackSession.template,
          message: 'Manual fallback session started'
        });

        res.json({
          taskId,
          fallbackSessionId: `fallback:${taskId}`,
          status: 'fallback_active',
          template: fallbackSession.template,
          message: 'Manual fallback session created successfully',
          expiresIn: 1800 // 30 minutes
        });

      } catch (error) {
        logger.error(`Error creating manual fallback for task ${taskId}:`, error);
        res.status(500).json({
          error: 'Failed to create manual fallback session',
          taskId
        });
      }
    }
  );

  /**
   * GET /api/v2/parse/validate/:taskId/history
   * PROMPT 2: Get validation history for a task
   */
  router.get('/:taskId/history', 
    param('taskId').isUUID().withMessage('Invalid task ID'),
    async (req, res) => {
      const { taskId } = req.params;

      try {
        const history = [];

        // Get different versions from cache
        const [original, validated, corrected, feedback] = await Promise.all([
          cache.get(`task:${taskId}`),
          cache.get(`task:${taskId}:validated`),
          cache.get(`task:${taskId}:corrected`),
          cache.get(`feedback:${taskId}`)
        ]);

        if (original) {
          history.push({
            version: 'original',
            timestamp: original.timestamp || original.cached_at,
            confidence: original.confidence,
            source: 'ai_extraction'
          });
        }

        if (validated) {
          history.push({
            version: 'validated',
            timestamp: validated.userValidation?.validatedAt,
            confidence: validated.confidence,
            source: 'user_validation',
            userId: validated.userValidation?.userId,
            fieldsValidated: validated.userValidation?.fieldsValidated?.length || 0
          });
        }

        if (corrected) {
          history.push({
            version: 'corrected',
            timestamp: corrected.lastModified,
            confidence: corrected.confidence,
            source: 'user_corrections',
            corrections: Object.keys(corrected.corrections || {})
          });
        }

        if (feedback) {
          history.push({
            version: 'feedback',
            timestamp: feedback.timestamp,
            satisfactionScore: feedback.satisfactionScore,
            source: 'user_feedback'
          });
        }

        res.json({
          taskId,
          history: history.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)),
          totalVersions: history.length
        });

      } catch (error) {
        logger.error(`Error getting validation history for ${taskId}:`, error);
        res.status(500).json({
          error: 'Failed to get validation history',
          taskId
        });
      }
    }
  );

  /**
   * Helper function to get default manual input template
   */
  function getDefaultTemplate() {
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

  return router;
}

module.exports = createValidationRoutes;
