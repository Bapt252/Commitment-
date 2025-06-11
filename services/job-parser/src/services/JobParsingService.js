/**
 * Job Parsing Service - AI-powered job description extraction
 * PROMPT 2: Ultra-optimized parser for job descriptions with NLP
 */

const OpenAI = require('openai');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const cheerio = require('cheerio');
const natural = require('natural');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs').promises;

const logger = require('../utils/logger');
const { createMinioClient } = require('../utils/storage');

class JobParsingService {
  constructor(options = {}) {
    this.cache = options.cache;
    this.openai = new OpenAI({
      apiKey: options.openai.apiKey
    });
    this.storage = createMinioClient(options.storage);
    
    // Initialize NLP tools
    this.initializeNLP();
    
    // Performance metrics
    this.metrics = {
      totalParsed: 0,
      averageTime: 0,
      cacheHits: 0,
      aiCalls: 0,
      nlpProcessings: 0
    };
  }

  /**
   * Initialize NLP processing tools
   */
  initializeNLP() {
    // Stemmer for French and English
    this.stemmerFr = natural.StemmerFr;
    this.stemmerEn = natural.PorterStemmer;
    
    // Tokenizer
    this.tokenizer = new natural.WordTokenizer();
    
    // Sentiment analyzer
    this.sentiment = new natural.SentimentAnalyzer('French', 
      natural.PorterStemmerFr, ['negation', 'dans']);
    
    logger.info('🧠 NLP tools initialized for job parsing');
  }

  /**
   * Parse job description with real-time streaming
   * PROMPT 2: <3 seconds with WebSocket feedback
   */
  async parseJob(file, options = {}) {
    const taskId = options.taskId || crypto.randomUUID();
    const startTime = Date.now();
    
    try {
      logger.info(`🚀 Starting job parsing for task ${taskId}`, {
        filename: file.originalname,
        size: file.size,
        mimetype: file.mimetype
      });

      // Progress callback for real-time updates
      const progress = options.progressCallback || (() => {});

      // Step 1: File validation and preparation (5%)
      progress({ taskId, status: 'processing', progress: 5, stage: 'validation' });
      await this.validateJobFile(file);

      // Step 2: Check cache for duplicate documents (10%)
      progress({ taskId, status: 'processing', progress: 10, stage: 'cache_check' });
      const cacheKey = await this.generateCacheKey(file);
      const cached = await this.cache.get(`job:${cacheKey}`);
      
      if (cached) {
        this.metrics.cacheHits++;
        logger.info(`⚡ Cache hit for job parsing task ${taskId}`);
        progress({ taskId, status: 'completed', progress: 100, data: cached, fromCache: true });
        return { taskId, data: cached, fromCache: true };
      }

      // Step 3: Extract raw text based on file type (25%)
      progress({ taskId, status: 'processing', progress: 15, stage: 'text_extraction' });
      const rawText = await this.extractJobText(file, (p) => {
        progress({ taskId, status: 'processing', progress: 15 + (p * 0.10), stage: 'text_extraction' });
      });

      // Step 4: NLP preprocessing (35%)
      progress({ taskId, status: 'processing', progress: 25, stage: 'nlp_processing' });
      const processedText = await this.preprocessJobText(rawText, (p) => {
        progress({ taskId, status: 'processing', progress: 25 + (p * 0.10), stage: 'nlp_processing' });
      });

      // Step 5: AI-powered structured extraction (75%)
      progress({ taskId, status: 'processing', progress: 35, stage: 'ai_analysis' });
      const structuredData = await this.extractJobStructuredData(processedText, rawText, (p) => {
        progress({ taskId, status: 'processing', progress: 35 + (p * 0.40), stage: 'ai_analysis' });
      });

      // Step 6: Confidence scoring and validation (95%)
      progress({ taskId, status: 'processing', progress: 75, stage: 'validation' });
      const finalData = await this.scoreAndValidateJob(structuredData, rawText, processedText);

      // Step 7: Cache results and finalize (100%)
      progress({ taskId, status: 'processing', progress: 95, stage: 'caching' });
      await this.cache.setex(`job:${cacheKey}`, 3600, finalData); // 1 hour cache

      const duration = Date.now() - startTime;
      this.updateMetrics(duration);

      logger.info(`✅ Job parsing completed for task ${taskId}`, {
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
      logger.error(`❌ Job parsing failed for task ${taskId}:`, error);
      
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
   * Extract text from various job file formats
   * PROMPT 2: Multi-format support including HTML
   */
  async extractJobText(file, progressCallback = () => {}) {
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

        case 'text/html':
          progressCallback(0.4);
          return await this.extractFromHTML(buffer);

        case 'text/plain':
          progressCallback(0.9);
          return buffer.toString('utf8');

        default:
          throw new Error(`Unsupported file format: ${mimetype}`);
      }
    } catch (error) {
      logger.error('Job text extraction failed:', error);
      throw new Error(`Failed to extract text: ${error.message}`);
    }
  }

  /**
   * Extract text from HTML job postings
   */
  async extractFromHTML(buffer) {
    try {
      const html = buffer.toString('utf8');
      const $ = cheerio.load(html);
      
      // Remove script and style elements
      $('script, style, nav, footer, header').remove();
      
      // Try to find main content areas
      const contentSelectors = [
        '.job-description',
        '.job-content',
        '.job-details',
        '#job-description',
        '[role="main"]',
        'main',
        '.content',
        'body'
      ];

      let text = '';
      for (const selector of contentSelectors) {
        const element = $(selector);
        if (element.length > 0) {
          text = element.text();
          break;
        }
      }

      if (!text) {
        text = $('body').text();
      }

      // Clean up whitespace
      return text.replace(/\s+/g, ' ').trim();

    } catch (error) {
      logger.error('HTML extraction failed:', error);
      throw new Error(`Failed to extract from HTML: ${error.message}`);
    }
  }

  /**
   * Extract text from PDF
   */
  async extractFromPDF(buffer, progressCallback) {
    try {
      progressCallback(0.4);
      const data = await pdfParse(buffer, {
        max: 20, // Max 20 pages for job descriptions
        version: 'v1.10.100'
      });

      progressCallback(1.0);
      return data.text;
    } catch (error) {
      logger.error('PDF extraction failed:', error);
      throw new Error(`Failed to extract from PDF: ${error.message}`);
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
   * NLP preprocessing for job descriptions
   * PROMPT 2: Enhanced NLP processing
   */
  async preprocessJobText(rawText, progressCallback = () => {}) {
    try {
      this.metrics.nlpProcessings++;
      progressCallback(0.2);

      // Tokenize text
      const tokens = this.tokenizer.tokenize(rawText.toLowerCase());
      progressCallback(0.4);

      // Remove stop words (French and English)
      const stopWordsFr = natural.stopwords;
      const stopWordsEn = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'];
      const allStopWords = [...stopWordsFr, ...stopWordsEn];
      
      const filteredTokens = tokens.filter(token => 
        !allStopWords.includes(token) && token.length > 2
      );
      progressCallback(0.6);

      // Stem words for better keyword extraction
      const stemmedTokens = filteredTokens.map(token => 
        this.stemmerFr.stem(token)
      );
      progressCallback(0.8);

      // Extract key phrases and entities
      const keyPhrases = this.extractKeyPhrases(rawText);
      const entities = this.extractEntities(rawText);
      progressCallback(1.0);

      return {
        originalText: rawText,
        tokens: filteredTokens,
        stemmedTokens,
        keyPhrases,
        entities,
        wordCount: tokens.length,
        uniqueWords: new Set(filteredTokens).size
      };

    } catch (error) {
      logger.error('NLP preprocessing failed:', error);
      throw new Error(`Failed to preprocess text: ${error.message}`);
    }
  }

  /**
   * Extract key phrases from job text
   */
  extractKeyPhrases(text) {
    // Common job-related phrases
    const jobPhrases = [
      /(\d+)\s*(?:ans?|années?)\s*(?:d['']?expérience|d['']?exp)/gi,
      /(?:salaire|rémunération|package)\s*:?\s*([€$]\s*\d+[k\s]*[-à]?\s*[€$]?\s*\d*[k\s]*)/gi,
      /(?:télétravail|remote|home\s*office|flex\s*office)/gi,
      /(?:CDI|CDD|stage|freelance|temps\s*plein|temps\s*partiel)/gi,
      /(?:startup|PME|grand\s*groupe|ETI|scale-up)/gi,
      /(?:bac\s*\+\s*\d+|master|ingénieur|doctorat)/gi
    ];

    const phrases = [];
    jobPhrases.forEach(regex => {
      const matches = text.match(regex);
      if (matches) {
        phrases.push(...matches);
      }
    });

    return phrases;
  }

  /**
   * Extract entities (companies, locations, technologies)
   */
  extractEntities(text) {
    const entities = {
      technologies: [],
      locations: [],
      companies: [],
      skills: []
    };

    // Technology keywords
    const techKeywords = [
      'javascript', 'python', 'java', 'react', 'angular', 'vue', 'node',
      'typescript', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift',
      'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform',
      'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch'
    ];

    // French cities
    const frenchCities = [
      'paris', 'lyon', 'marseille', 'toulouse', 'lille', 'bordeaux',
      'nantes', 'strasbourg', 'montpellier', 'rennes', 'grenoble',
      'dijon', 'angers', 'nîmes', 'villeurbanne', 'clermont-ferrand'
    ];

    const lowerText = text.toLowerCase();

    // Extract technologies
    techKeywords.forEach(tech => {
      if (lowerText.includes(tech)) {
        entities.technologies.push(tech);
      }
    });

    // Extract locations
    frenchCities.forEach(city => {
      if (lowerText.includes(city)) {
        entities.locations.push(city);
      }
    });

    return entities;
  }

  /**
   * AI-powered structured data extraction
   * PROMPT 2: OpenAI integration for job parsing
   */
  async extractJobStructuredData(processedText, originalText, progressCallback = () => {}) {
    try {
      this.metrics.aiCalls++;
      progressCallback(0.1);

      const prompt = this.buildJobExtractionPrompt(originalText, processedText);
      progressCallback(0.3);

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `Tu es un expert en analyse de fiches de poste. Extrais les informations suivantes de l'offre d'emploi en français avec une précision maximale. Réponds UNIQUEMENT en JSON valide.`
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
      logger.error('AI job extraction failed:', error);
      throw new Error(`Failed to extract structured data: ${error.message}`);
    }
  }

  /**
   * Build job extraction prompt
   * PROMPT 2: Targeted extraction for job specifications
   */
  buildJobExtractionPrompt(originalText, processedText) {
    return `
Extrais les informations suivantes de cette fiche de poste en JSON avec cette structure exacte :

{
  "position": {
    "title": "string",
    "level": "junior|mid|senior|lead|director",
    "department": "string",
    "type": "CDI|CDD|Stage|Freelance|Temps partiel"
  },
  "requirements": {
    "skills_required": ["array of required skills"],
    "skills_preferred": ["array of preferred skills"],
    "experience_min": "nombre d'années requis",
    "education": "string",
    "languages": [
      {"language": "string", "level": "débutant|intermédiaire|avancé|courant|natif"}
    ]
  },
  "location": {
    "city": "string",
    "remote_work": "none|partial|full",
    "travel_required": "boolean"
  },
  "compensation": {
    "salary_min": "number or null",
    "salary_max": "number or null",
    "salary_period": "annual|monthly|daily|hourly",
    "benefits": ["array of benefits"]
  },
  "company": {
    "name": "string",
    "size": "startup|PME|ETI|grand groupe",
    "sector": "string",
    "description": "string"
  },
  "details": {
    "start_date": "string or immediate",
    "application_deadline": "string or null",
    "contact_person": "string or null",
    "mission_description": "string"
  }
}

Fiche de poste:
${originalText.substring(0, 10000)}

Mots-clés identifiés: ${processedText.keyPhrases?.join(', ') || 'N/A'}
Technologies détectées: ${processedText.entities?.technologies?.join(', ') || 'N/A'}
`;
  }

  /**
   * Score confidence and validate extracted job data
   * PROMPT 2: 97%+ confidence target
   */
  async scoreAndValidateJob(extractedData, originalText, processedText) {
    const confidence = this.calculateJobConfidence(extractedData, originalText, processedText);
    
    const validatedData = {
      data: extractedData,
      confidence: confidence,
      suggestions: this.generateJobSuggestions(extractedData, confidence),
      fallback_required: confidence < 0.85,
      analysis: {
        wordCount: processedText.wordCount,
        uniqueWords: processedText.uniqueWords,
        keyPhrasesFound: processedText.keyPhrases?.length || 0,
        technologiesDetected: processedText.entities?.technologies?.length || 0,
        locationsDetected: processedText.entities?.locations?.length || 0
      }
    };

    return validatedData;
  }

  /**
   * Calculate confidence score for job parsing
   */
  calculateJobConfidence(data, originalText, processedText) {
    let score = 0;
    let maxScore = 0;

    // Position information (25% weight)
    const position = data.position || {};
    maxScore += 25;
    if (position.title && position.title.trim().length > 0) score += 15;
    if (position.level) score += 5;
    if (position.type) score += 5;

    // Requirements (30% weight)
    maxScore += 30;
    const requirements = data.requirements || {};
    if (requirements.skills_required && requirements.skills_required.length > 0) {
      score += Math.min(15, requirements.skills_required.length * 3);
    }
    if (requirements.experience_min) score += 10;
    if (requirements.education) score += 5;

    // Location (15% weight)
    maxScore += 15;
    const location = data.location || {};
    if (location.city) score += 10;
    if (location.remote_work) score += 5;

    // Company (15% weight)
    maxScore += 15;
    const company = data.company || {};
    if (company.name) score += 10;
    if (company.sector) score += 5;

    // Details (15% weight)
    maxScore += 15;
    const details = data.details || {};
    if (details.mission_description && details.mission_description.length > 50) score += 10;
    if (details.start_date) score += 3;
    if (details.contact_person) score += 2;

    return Math.min(1.0, score / maxScore);
  }

  /**
   * Generate validation suggestions for job data
   */
  generateJobSuggestions(data, confidence) {
    const suggestions = [];

    if (!data.position?.title) {
      suggestions.push({
        field: 'position.title',
        message: 'Titre de poste manquant - vérification nécessaire',
        priority: 'high'
      });
    }

    if (!data.requirements?.skills_required || data.requirements.skills_required.length === 0) {
      suggestions.push({
        field: 'requirements.skills_required',
        message: 'Compétences requises non détectées - vérification requise',
        priority: 'high'
      });
    }

    if (!data.location?.city) {
      suggestions.push({
        field: 'location.city',
        message: 'Localisation non précisée - important pour les candidats',
        priority: 'medium'
      });
    }

    if (confidence < 0.9 && (!data.compensation?.salary_min && !data.compensation?.salary_max)) {
      suggestions.push({
        field: 'compensation',
        message: 'Informations salariales manquantes - peut réduire l\'attractivité',
        priority: 'low'
      });
    }

    if (!data.company?.name) {
      suggestions.push({
        field: 'company.name',
        message: 'Nom de l\'entreprise non détecté',
        priority: 'medium'
      });
    }

    return suggestions;
  }

  /**
   * Validate uploaded job file
   */
  async validateJobFile(file) {
    const maxSize = 5 * 1024 * 1024; // 5MB for job descriptions
    const supportedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/html',
      'text/plain'
    ];

    if (file.size > maxSize) {
      throw new Error('File size exceeds 5MB limit');
    }

    if (!supportedTypes.includes(file.mimetype)) {
      throw new Error(`Unsupported file type: ${file.mimetype}`);
    }
  }

  /**
   * Generate cache key for job file
   */
  async generateCacheKey(file) {
    const hash = crypto.createHash('sha256');
    hash.update(file.buffer);
    hash.update(file.originalname);
    hash.update(file.size.toString());
    return hash.digest('hex');
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
        this.metrics.cacheHits / this.metrics.totalParsed : 0,
      nlpProcessingRate: this.metrics.nlpProcessings / this.metrics.totalParsed || 0
    };
  }
}

module.exports = JobParsingService;
