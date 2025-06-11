/**
 * Validation Service - Interactive validation and corrections
 * PROMPT 2: 95%+ user satisfaction without corrections target
 */

const Joi = require('joi');
const logger = require('../utils/logger');

class ValidationService {
  constructor(options = {}) {
    this.cache = options.cache;
    this.validationRules = this.setupValidationRules();
    this.metrics = {
      validationsProcessed: 0,
      correctionsApplied: 0,
      userSatisfactionScore: 0,
      avgCorrectionsPerTask: 0
    };
  }

  /**
   * Setup validation rules for CV data
   * PROMPT 2: Comprehensive validation schema
   */
  setupValidationRules() {
    return {
      personal: Joi.object({
        firstName: Joi.string().min(1).max(100).trim(),
        lastName: Joi.string().min(1).max(100).trim(),
        title: Joi.string().max(200).trim().allow(''),
        email: Joi.string().email().trim().allow(''),
        phone: Joi.string().pattern(/^[\+]?[0-9\s\-\(\)\.]+$/).max(20).allow(''),
        address: Joi.string().max(500).trim().allow('')
      }),

      skills: Joi.object({
        technical: Joi.array().items(Joi.string().max(100)),
        soft: Joi.array().items(Joi.string().max(100)),
        software: Joi.array().items(Joi.object({
          name: Joi.string().max(100).required(),
          level: Joi.string().valid('débutant', 'intermédiaire', 'avancé', 'expert').required()
        }))
      }),

      languages: Joi.array().items(Joi.object({
        language: Joi.string().max(50).required(),
        level: Joi.string().valid('A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'natif').required()
      })),

      certifications: Joi.array().items(Joi.string().max(200)),

      experience: Joi.array().items(Joi.object({
        position: Joi.string().max(200).required(),
        company: Joi.string().max(200).required(),
        location: Joi.string().max(200).allow(''),
        startDate: Joi.string().pattern(/^\d{4}-\d{2}$/).required(),
        endDate: Joi.string().pattern(/^\d{4}-\d{2}$|^current$/).required(),
        description: Joi.string().max(2000).allow(''),
        technologies: Joi.array().items(Joi.string().max(100))
      })),

      education: Joi.array().items(Joi.object({
        degree: Joi.string().max(200).required(),
        institution: Joi.string().max(200).required(),
        location: Joi.string().max(200).allow(''),
        graduationDate: Joi.string().pattern(/^\d{4}-\d{2}$/).allow(''),
        grade: Joi.string().max(50).allow('')
      }))
    };
  }

  /**
   * Process user validation for extracted CV data
   * PROMPT 2: Interactive validation with user feedback
   */
  async processValidation(options = {}) {
    const { taskId, validatedFields, corrections, userId } = options;
    
    try {
      logger.info(`📝 Processing validation for task ${taskId}`, {
        userId,
        fieldsCount: Object.keys(validatedFields || {}).length,
        correctionsCount: Object.keys(corrections || {}).length
      });

      // Get original parsed data
      const originalData = await this.cache.get(`cv:task:${taskId}`);
      if (!originalData) {
        throw new Error('Original task data not found');
      }

      // Merge validated fields with original data
      const mergedData = this.mergeValidatedData(originalData.data, validatedFields);

      // Apply user corrections
      const correctedData = this.applyUserCorrections(mergedData, corrections);

      // Validate the corrected data
      const validationResult = await this.validateCVData(correctedData);

      // Calculate user satisfaction score
      const satisfactionScore = this.calculateSatisfactionScore(
        originalData.data,
        correctedData,
        corrections
      );

      // Prepare final result
      const result = {
        taskId,
        data: correctedData,
        validation: validationResult,
        userValidation: {
          userId,
          validatedAt: new Date().toISOString(),
          fieldsValidated: Object.keys(validatedFields || {}),
          correctionsApplied: Object.keys(corrections || {}),
          satisfactionScore
        },
        confidence: this.calculatePostValidationConfidence(validationResult, satisfactionScore),
        status: 'user_validated'
      };

      // Cache the validated result
      await this.cache.setex(`cv:task:${taskId}:validated`, 3600, result);

      // Update metrics
      this.updateValidationMetrics(corrections, satisfactionScore);

      logger.info(`✅ Validation processed for task ${taskId}`, {
        confidence: result.confidence,
        satisfactionScore,
        errorsFound: validationResult.errors.length
      });

      return result;

    } catch (error) {
      logger.error(`❌ Validation failed for task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Apply user corrections to CV data
   * PROMPT 2: Real-time corrections with smart merging
   */
  async applyCorrections(options = {}) {
    const { taskId, corrections, field, userId } = options;

    try {
      logger.info(`🔧 Applying corrections for task ${taskId}`, {
        field,
        userId,
        correctionsKeys: Object.keys(corrections)
      });

      // Get current data
      const currentData = await this.cache.get(`cv:task:${taskId}:validated`) ||
                          await this.cache.get(`cv:task:${taskId}`);
      
      if (!currentData) {
        throw new Error('Task data not found for corrections');
      }

      // Apply field-specific corrections
      const updatedData = this.applyFieldCorrections(currentData.data, field, corrections);

      // Re-validate the updated data
      const validationResult = await this.validateCVData(updatedData);

      // Prepare corrected result
      const result = {
        ...currentData,
        data: updatedData,
        validation: validationResult,
        corrections: {
          ...(currentData.corrections || {}),
          [field]: {
            appliedAt: new Date().toISOString(),
            appliedBy: userId,
            corrections
          }
        },
        lastModified: new Date().toISOString()
      };

      // Update cache
      await this.cache.setex(`cv:task:${taskId}:corrected`, 3600, result);

      // Update metrics
      this.metrics.correctionsApplied++;

      logger.info(`✅ Corrections applied for task ${taskId}, field: ${field}`);

      return result;

    } catch (error) {
      logger.error(`❌ Corrections failed for task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Validate CV data against schema
   */
  async validateCVData(data) {
    const errors = [];
    const warnings = [];
    const suggestions = [];

    try {
      // Validate each section
      for (const [section, schema] of Object.entries(this.validationRules)) {
        if (data[section]) {
          const { error } = schema.validate(data[section], { abortEarly: false });
          
          if (error) {
            error.details.forEach(detail => {
              errors.push({
                section,
                field: detail.path.join('.'),
                message: detail.message,
                value: detail.context?.value,
                type: 'validation_error'
              });
            });
          }
        }
      }

      // Custom business logic validations
      this.validateBusinessRules(data, errors, warnings, suggestions);

      return {
        isValid: errors.length === 0,
        errors,
        warnings,
        suggestions,
        score: this.calculateValidationScore(errors, warnings),
        validatedAt: new Date().toISOString()
      };

    } catch (error) {
      logger.error('Validation error:', error);
      return {
        isValid: false,
        errors: [{ type: 'system_error', message: error.message }],
        warnings: [],
        suggestions: []
      };
    }
  }

  /**
   * Apply business rules validation
   */
  validateBusinessRules(data, errors, warnings, suggestions) {
    // Required fields check
    if (!data.personal?.firstName || !data.personal?.lastName) {
      errors.push({
        section: 'personal',
        field: 'name',
        message: 'Nom et prénom sont obligatoires',
        type: 'required_field'
      });
    }

    // Email format validation
    if (data.personal?.email && !this.isValidEmail(data.personal.email)) {
      errors.push({
        section: 'personal',
        field: 'email',
        message: 'Format d\'email invalide',
        type: 'format_error'
      });
    }

    // Phone number validation
    if (data.personal?.phone && !this.isValidPhone(data.personal.phone)) {
      warnings.push({
        section: 'personal',
        field: 'phone',
        message: 'Format de téléphone suspect - vérification recommandée',
        type: 'format_warning'
      });
    }

    // Experience date validation
    if (data.experience) {
      data.experience.forEach((exp, index) => {
        if (exp.startDate && exp.endDate && exp.endDate !== 'current') {
          if (new Date(exp.startDate) >= new Date(exp.endDate)) {
            errors.push({
              section: 'experience',
              field: `experience[${index}].dates`,
              message: 'Date de fin antérieure à la date de début',
              type: 'date_error'
            });
          }
        }
      });
    }

    // Education date validation
    if (data.education) {
      data.education.forEach((edu, index) => {
        if (edu.graduationDate) {
          const gradYear = parseInt(edu.graduationDate.split('-')[0]);
          const currentYear = new Date().getFullYear();
          
          if (gradYear > currentYear + 10) {
            warnings.push({
              section: 'education',
              field: `education[${index}].graduationDate`,
              message: 'Date de diplôme dans le futur - vérification nécessaire',
              type: 'date_warning'
            });
          }
        }
      });
    }

    // Skills validation
    if (!data.skills?.technical || data.skills.technical.length === 0) {
      suggestions.push({
        section: 'skills',
        field: 'technical',
        message: 'Aucune compétence technique détectée - ajout recommandé',
        type: 'completeness_suggestion'
      });
    }

    // Languages validation
    if (!data.languages || data.languages.length === 0) {
      suggestions.push({
        section: 'languages',
        field: 'languages',
        message: 'Aucune langue mentionnée - ajout recommandé pour améliorer le profil',
        type: 'completeness_suggestion'
      });
    }
  }

  /**
   * Merge validated fields with original data
   */
  mergeValidatedData(originalData, validatedFields) {
    if (!validatedFields) return originalData;

    const merged = JSON.parse(JSON.stringify(originalData));

    for (const [fieldPath, value] of Object.entries(validatedFields)) {
      this.setNestedProperty(merged, fieldPath, value);
    }

    return merged;
  }

  /**
   * Apply user corrections to specific field
   */
  applyFieldCorrections(data, field, corrections) {
    const updated = JSON.parse(JSON.stringify(data));

    if (field && corrections) {
      this.setNestedProperty(updated, field, corrections);
    } else {
      // Apply all corrections
      for (const [fieldPath, value] of Object.entries(corrections)) {
        this.setNestedProperty(updated, fieldPath, value);
      }
    }

    return updated;
  }

  /**
   * Apply user corrections to data
   */
  applyUserCorrections(data, corrections) {
    if (!corrections) return data;

    const corrected = JSON.parse(JSON.stringify(data));

    for (const [fieldPath, value] of Object.entries(corrections)) {
      this.setNestedProperty(corrected, fieldPath, value);
    }

    return corrected;
  }

  /**
   * Set nested property using dot notation
   */
  setNestedProperty(obj, path, value) {
    const keys = path.split('.');
    let current = obj;

    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current)) {
        current[key] = {};
      }
      current = current[key];
    }

    current[keys[keys.length - 1]] = value;
  }

  /**
   * Calculate user satisfaction score
   * PROMPT 2: Target 95%+ validation without corrections
   */
  calculateSatisfactionScore(originalData, correctedData, corrections) {
    const totalFields = this.countFields(originalData);
    const correctionsCount = Object.keys(corrections || {}).length;
    
    if (totalFields === 0) return 0;

    // Base score starts high if few corrections needed
    let score = Math.max(0, 100 - (correctionsCount / totalFields * 100));

    // Bonus for completeness
    const completenessBonus = this.calculateCompleteness(correctedData) * 10;
    score += completenessBonus;

    // Penalty for critical field corrections
    const criticalCorrections = this.countCriticalCorrections(corrections);
    score -= criticalCorrections * 15;

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Calculate post-validation confidence
   */
  calculatePostValidationConfidence(validationResult, satisfactionScore) {
    let confidence = 0.7; // Base confidence after validation

    // Boost confidence if no errors
    if (validationResult.isValid) {
      confidence += 0.2;
    }

    // Add satisfaction score impact
    confidence += (satisfactionScore / 100) * 0.1;

    // Reduce confidence for warnings
    confidence -= validationResult.warnings.length * 0.02;

    return Math.max(0, Math.min(1, confidence));
  }

  /**
   * Calculate validation score
   */
  calculateValidationScore(errors, warnings) {
    let score = 100;
    score -= errors.length * 15; // -15 points per error
    score -= warnings.length * 5; // -5 points per warning
    return Math.max(0, score);
  }

  /**
   * Count total fields in data
   */
  countFields(data) {
    let count = 0;
    
    const countInObject = (obj) => {
      for (const value of Object.values(obj)) {
        if (Array.isArray(value)) {
          count += value.length;
        } else if (typeof value === 'object' && value !== null) {
          countInObject(value);
        } else {
          count++;
        }
      }
    };

    countInObject(data);
    return count;
  }

  /**
   * Calculate completeness percentage
   */
  calculateCompleteness(data) {
    const requiredFields = [
      'personal.firstName',
      'personal.lastName',
      'personal.email'
    ];

    const optionalFields = [
      'personal.phone',
      'personal.title',
      'skills.technical',
      'experience',
      'education'
    ];

    let score = 0;
    let total = requiredFields.length + optionalFields.length;

    // Check required fields (higher weight)
    for (const field of requiredFields) {
      if (this.getNestedProperty(data, field)) {
        score += 2; // Required fields worth 2 points
      }
      total += 1; // Adjust total for higher weight
    }

    // Check optional fields
    for (const field of optionalFields) {
      const value = this.getNestedProperty(data, field);
      if (value && (Array.isArray(value) ? value.length > 0 : true)) {
        score += 1;
      }
    }

    return score / total;
  }

  /**
   * Count critical corrections
   */
  countCriticalCorrections(corrections) {
    if (!corrections) return 0;

    const criticalFields = [
      'personal.firstName',
      'personal.lastName',
      'personal.email'
    ];

    return Object.keys(corrections).filter(field => 
      criticalFields.includes(field)
    ).length;
  }

  /**
   * Get nested property using dot notation
   */
  getNestedProperty(obj, path) {
    return path.split('.').reduce((current, key) => 
      current && current[key] !== undefined ? current[key] : null, obj);
  }

  /**
   * Validate email format
   */
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate phone format
   */
  isValidPhone(phone) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)\.]{8,20}$/;
    return phoneRegex.test(phone);
  }

  /**
   * Update validation metrics
   */
  updateValidationMetrics(corrections, satisfactionScore) {
    this.metrics.validationsProcessed++;
    
    if (corrections) {
      const correctionCount = Object.keys(corrections).length;
      this.metrics.avgCorrectionsPerTask = (
        (this.metrics.avgCorrectionsPerTask * (this.metrics.validationsProcessed - 1) + correctionCount) /
        this.metrics.validationsProcessed
      );
    }

    this.metrics.userSatisfactionScore = (
      (this.metrics.userSatisfactionScore * (this.metrics.validationsProcessed - 1) + satisfactionScore) /
      this.metrics.validationsProcessed
    );
  }

  /**
   * Get validation service statistics
   * PROMPT 2: Monitor 95%+ satisfaction target
   */
  getStats() {
    return {
      ...this.metrics,
      targets: {
        userSatisfaction: {
          current: Math.round(this.metrics.userSatisfactionScore),
          target: 95,
          status: this.metrics.userSatisfactionScore >= 95 ? 'ACHIEVED' : 'BELOW_TARGET'
        },
        avgCorrections: {
          current: Math.round(this.metrics.avgCorrectionsPerTask * 100) / 100,
          target: 2,
          status: this.metrics.avgCorrectionsPerTask <= 2 ? 'ACHIEVED' : 'ABOVE_TARGET'
        }
      }
    };
  }

  /**
   * Generate smart suggestions for improvement
   */
  generateSmartSuggestions(data, validationResult) {
    const suggestions = [...validationResult.suggestions];

    // Add AI-powered suggestions based on patterns
    if (data.experience && data.experience.length > 0) {
      const hasRecentExperience = data.experience.some(exp => 
        exp.endDate === 'current' || new Date(exp.endDate).getFullYear() >= new Date().getFullYear() - 2
      );

      if (!hasRecentExperience) {
        suggestions.push({
          type: 'career_gap',
          message: 'Il semble y avoir un écart dans l\'expérience récente - vérifiez les dates',
          priority: 'medium'
        });
      }
    }

    // Technology stack suggestions
    if (data.skills?.technical) {
      const modernTechs = ['React', 'Vue.js', 'Python', 'JavaScript', 'TypeScript', 'Docker', 'Kubernetes'];
      const hasModernTech = data.skills.technical.some(skill => 
        modernTechs.some(tech => skill.toLowerCase().includes(tech.toLowerCase()))
      );

      if (!hasModernTech) {
        suggestions.push({
          type: 'skills_modernization',
          message: 'Considérez ajouter des technologies modernes pour améliorer l\'attractivité du profil',
          priority: 'low'
        });
      }
    }

    return suggestions;
  }
}

module.exports = ValidationService;
