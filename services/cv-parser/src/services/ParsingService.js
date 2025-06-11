/**
 * Parsing Service - Core AI-powered CV extraction
 * PROMPT 2: Ultra-optimized parser with OpenAI, OCR, and real-time streaming
 */

const OpenAI = require('openai');
const Tesseract = require('tesseract.js');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const sharp = require('sharp');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs').promises;

const logger = require('../utils/logger');
const { createMinioClient } = require('../utils/storage');

class ParsingService {
  constructor(options = {}) {
    this.cache = options.cache;
    this.openai = new OpenAI({
      apiKey: options.openai.apiKey
    });
    this.storage = createMinioClient(options.storage);
    
    // Performance metrics
    this.metrics = {
      totalParsed: 0,
      averageTime: 0,
      cacheHits: 0,
      aiCalls: 0,
      ocrCalls: 0
    };
  }

  /**
   * Parse CV with real-time streaming
   * PROMPT 2: <3 seconds with WebSocket feedback
   */
  async parseCV(file, options = {}) {
    const taskId = options.taskId || crypto.randomUUID();
    const startTime = Date.now();
    
    try {
      logger.info(`🚀 Starting CV parsing for task ${taskId}`, {
        filename: file.originalname,
        size: file.size,
        mimetype: file.mimetype
      });

      // Progress callback for real-time updates
      const progress = options.progressCallback || (() => {});

      // Step 1: File validation and preparation (5%)
      progress({ taskId, status: 'processing', progress: 5, stage: 'validation' });
      await this.validateFile(file);

      // Step 2: Check cache for duplicate documents (10%)
      progress({ taskId, status: 'processing', progress: 10, stage: 'cache_check' });
      const cacheKey = await this.generateCacheKey(file);
      const cached = await this.cache.get(`cv:${cacheKey}`);
      
      if (cached) {
        this.metrics.cacheHits++;
        logger.info(`⚡ Cache hit for task ${taskId}`);
        progress({ taskId, status: 'completed', progress: 100, data: cached, fromCache: true });
        return { taskId, data: cached, fromCache: true };
      }

      // Step 3: Extract raw text based on file type (30%)
      progress({ taskId, status: 'processing', progress: 15, stage: 'text_extraction' });
      const rawText = await this.extractText(file, (p) => {
        progress({ taskId, status: 'processing', progress: 15 + (p * 0.15), stage: 'text_extraction' });
      });

      // Step 4: AI-powered structured extraction (70%)
      progress({ taskId, status: 'processing', progress: 30, stage: 'ai_analysis' });
      const structuredData = await this.extractStructuredData(rawText, (p) => {
        progress({ taskId, status: 'processing', progress: 30 + (p * 0.60), stage: 'ai_analysis' });
      });

      // Step 5: Confidence scoring and validation (95%)
      progress({ taskId, status: 'processing', progress: 90, stage: 'validation' });
      const finalData = await this.scoreAndValidate(structuredData, rawText);

      // Step 6: Cache results and finalize (100%)
      progress({ taskId, status: 'processing', progress: 95, stage: 'caching' });
      await this.cache.setex(`cv:${cacheKey}`, 3600, finalData); // 1 hour cache

      const duration = Date.now() - startTime;
      this.updateMetrics(duration);

      logger.info(`✅ CV parsing completed for task ${taskId}`, {
        duration: `${duration}ms`,
        confidence: finalData.confidence,
        fieldsExtracted: Object.keys(finalData.data).length
      });

      progress({ 
        taskId, 
        status: 'completed', 
        progress: 100, 
        data: finalData,
        duration,
        confidence: finalData.confidence
      });

      return { taskId, data: finalData, duration };

    } catch (error) {
      logger.error(`❌ CV parsing failed for task ${taskId}:`, error);
      
      if (options.progressCallback) {
        options.progressCallback({
          taskId,
          status: 'error',
          error: error.message,
          fallback_required: true
        });
      }

      throw error;
    }
  }

  /**
   * Extract text from various file formats
   * PROMPT 2: Multi-format support with OCR
   */
  async extractText(file, progressCallback = () => {}) {
    const { mimetype, buffer } = file;

    try {
      switch (mimetype) {
        case 'application/pdf':
          progressCallback(0.2);
          return await this.extractFromPDF(buffer, progressCallback);

        case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        case 'application/msword':
          progressCallback(0.3);
          return await this.extractFromWord(buffer);

        case 'image/jpeg':
        case 'image/png':
        case 'image/jpg':
          progressCallback(0.1);
          return await this.extractFromImage(buffer, progressCallback);

        case 'text/plain':
          progressCallback(0.9);
          return buffer.toString('utf8');

        default:
          throw new Error(`Unsupported file format: ${mimetype}`);
      }
    } catch (error) {
      logger.error('Text extraction failed:', error);
      throw new Error(`Failed to extract text: ${error.message}`);
    }
  }

  /**
   * Extract text from PDF with fallback to OCR
   */
  async extractFromPDF(buffer, progressCallback) {
    try {
      progressCallback(0.4);
      const data = await pdfParse(buffer, {
        max: 50, // Max 50 pages
        version: 'v1.10.100'
      });

      progressCallback(0.8);
      
      // If text extraction yields very little content, try OCR
      if (data.text.trim().length < 100) {
        logger.info('PDF text extraction yielded minimal content, trying OCR...');
        return await this.extractFromImage(buffer, progressCallback);
      }

      progressCallback(1.0);
      return data.text;
    } catch (error) {
      logger.warn('PDF text extraction failed, falling back to OCR:', error.message);
      return await this.extractFromImage(buffer, progressCallback);
    }
  }

  /**
   * Extract text from Word documents
   */
  async extractFromWord(buffer) {
    try {
      const result = await mammoth.extractRawText({ buffer });
      return result.value;
    } catch (error) {
      logger.error('Word extraction failed:', error);
      throw new Error(`Failed to extract from Word document: ${error.message}`);
    }
  }

  /**
   * Extract text from images using OCR
   * PROMPT 2: High-performance OCR
   */
  async extractFromImage(buffer, progressCallback = () => {}) {
    try {
      this.metrics.ocrCalls++;
      
      progressCallback(0.2);
      
      // Preprocess image for better OCR
      const processedImage = await sharp(buffer)
        .resize({ width: 2000, height: 2000, fit: 'inside', withoutEnlargement: true })
        .grayscale()
        .normalize()
        .sharpen()
        .toBuffer();

      progressCallback(0.4);

      // Perform OCR with Tesseract
      const { data: { text } } = await Tesseract.recognize(processedImage, 'fra+eng', {
        logger: (m) => {
          if (m.status === 'recognizing text') {
            progressCallback(0.4 + (m.progress * 0.5));
          }
        },
        tessedit_pageseg_mode: '1', // Automatic page segmentation with OSD
        tessedit_ocr_engine_mode: '2', // Neural nets LSTM engine
      });

      progressCallback(1.0);
      
      if (!text || text.trim().length < 50) {
        throw new Error('OCR extraction yielded insufficient text');
      }

      return text;
    } catch (error) {
      logger.error('OCR extraction failed:', error);
      throw new Error(`Failed to extract text from image: ${error.message}`);
    }
  }

  /**
   * AI-powered structured data extraction
   * PROMPT 2: OpenAI integration with confidence scoring
   */
  async extractStructuredData(rawText, progressCallback = () => {}) {
    try {
      this.metrics.aiCalls++;
      progressCallback(0.1);

      const prompt = this.buildExtractionPrompt(rawText);
      progressCallback(0.3);

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `Tu es un expert en extraction de données CV. Extraie les informations suivantes du CV en français avec une précision maximale. Réponds UNIQUEMENT en JSON valide.`
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.1,
        max_tokens: 2000,
        response_format: { type: "json_object" }
      });

      progressCallback(0.8);

      const extractedData = JSON.parse(response.choices[0].message.content);
      progressCallback(1.0);

      return extractedData;
    } catch (error) {
      logger.error('AI extraction failed:', error);
      throw new Error(`Failed to extract structured data: ${error.message}`);
    }
  }

  /**
   * Build optimized extraction prompt
   * PROMPT 2: Targeted extraction as specified
   */
  buildExtractionPrompt(text) {
    return `
Extrais les informations suivantes du CV en JSON avec cette structure exacte :

{
  "personal": {
    "firstName": "string",
    "lastName": "string", 
    "title": "string",
    "email": "string",
    "phone": "string",
    "address": "string"
  },
  "skills": {
    "technical": ["array of technical skills"],
    "soft": ["array of soft skills"],
    "software": [
      {"name": "string", "level": "débutant|intermédiaire|avancé|expert"}
    ]
  },
  "languages": [
    {"language": "string", "level": "A1|A2|B1|B2|C1|C2|natif"}
  ],
  "certifications": ["array of certifications"],
  "experience": [
    {
      "position": "string",
      "company": "string", 
      "location": "string",
      "startDate": "YYYY-MM",
      "endDate": "YYYY-MM or current",
      "description": "string",
      "technologies": ["array"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "location": "string", 
      "graduationDate": "YYYY-MM",
      "grade": "string"
    }
  ]
}

CV Text:
${text.substring(0, 8000)}
`;
  }

  /**
   * Score confidence and validate extracted data
   * PROMPT 2: 97%+ confidence target
   */
  async scoreAndValidate(extractedData, originalText) {
    const confidence = this.calculateConfidence(extractedData, originalText);
    
    const validatedData = {
      data: extractedData,
      confidence: confidence,
      suggestions: this.generateSuggestions(extractedData, confidence),
      fallback_required: confidence < 0.85
    };

    return validatedData;
  }

  /**
   * Calculate confidence score based on completeness and validation
   */
  calculateConfidence(data, originalText) {
    let score = 0;
    let maxScore = 0;

    // Personal information (30% weight)
    const personal = data.personal || {};
    const personalFields = ['firstName', 'lastName', 'email', 'phone'];
    personalFields.forEach(field => {
      maxScore += 7.5;
      if (personal[field] && personal[field].trim().length > 0) {
        score += 7.5;
      }
    });

    // Experience (25% weight)
    maxScore += 25;
    if (data.experience && data.experience.length > 0) {
      score += Math.min(25, data.experience.length * 8);
    }

    // Skills (20% weight)
    maxScore += 20;
    const skillsCount = (data.skills?.technical?.length || 0) + (data.skills?.soft?.length || 0);
    if (skillsCount > 0) {
      score += Math.min(20, skillsCount * 2);
    }

    // Education (15% weight)  
    maxScore += 15;
    if (data.education && data.education.length > 0) {
      score += Math.min(15, data.education.length * 7);
    }

    // Languages (10% weight)
    maxScore += 10;
    if (data.languages && data.languages.length > 0) {
      score += Math.min(10, data.languages.length * 3);
    }

    return Math.min(1.0, score / maxScore);
  }

  /**
   * Generate validation suggestions
   */
  generateSuggestions(data, confidence) {
    const suggestions = [];

    if (!data.personal?.firstName || !data.personal?.lastName) {
      suggestions.push({
        field: 'personal.name',
        message: 'Nom et prénom incomplets - vérification nécessaire',
        priority: 'high'
      });
    }

    if (!data.personal?.email) {
      suggestions.push({
        field: 'personal.email',
        message: 'Email manquant - important pour contact',
        priority: 'high'
      });
    }

    if (confidence < 0.9 && (!data.experience || data.experience.length === 0)) {
      suggestions.push({
        field: 'experience',
        message: 'Expérience professionnelle non détectée - vérification requise',
        priority: 'medium'
      });
    }

    if (!data.skills?.technical || data.skills.technical.length < 3) {
      suggestions.push({
        field: 'skills.technical',
        message: 'Peu de compétences techniques détectées',
        priority: 'low'
      });
    }

    return suggestions;
  }

  /**
   * Generate cache key for duplicate detection
   * PROMPT 2: 85%+ cache hit ratio target
   */
  async generateCacheKey(file) {
    const hash = crypto.createHash('sha256');
    hash.update(file.buffer);
    hash.update(file.originalname);
    hash.update(file.size.toString());
    return hash.digest('hex');
  }

  /**
   * Validate uploaded file
   */
  async validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const supportedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'image/jpeg',
      'image/png',
      'image/jpg',
      'text/plain'
    ];

    if (file.size > maxSize) {
      throw new Error('File size exceeds 10MB limit');
    }

    if (!supportedTypes.includes(file.mimetype)) {
      throw new Error(`Unsupported file type: ${file.mimetype}`);
    }
  }

  /**
   * Update performance metrics
   */
  updateMetrics(duration) {
    this.metrics.totalParsed++;
    this.metrics.averageTime = (
      (this.metrics.averageTime * (this.metrics.totalParsed - 1) + duration) / 
      this.metrics.totalParsed
    );
  }

  /**
   * Get service statistics
   */
  getStats() {
    return {
      ...this.metrics,
      cacheHitRate: this.metrics.totalParsed > 0 ? 
        this.metrics.cacheHits / this.metrics.totalParsed : 0
    };
  }
}

module.exports = ParsingService;
