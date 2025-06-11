/**
 * Upload Middleware - File upload handling for CV Parser Ultra v2.0
 * PROMPT 2: Multi-format support up to 10MB with validation
 */

const multer = require('multer');
const path = require('path');
const crypto = require('crypto');
const fs = require('fs').promises;

const config = require('../config/config');
const logger = require('../utils/logger');

class UploadMiddleware {
  constructor() {
    this.setupStorage();
    this.setupMulter();
  }

  setupStorage() {
    // Memory storage for processing (files stored in memory for faster access)
    this.memoryStorage = multer.memoryStorage();

    // Disk storage for temporary files (fallback)
    this.diskStorage = multer.diskStorage({
      destination: async (req, file, cb) => {
        try {
          // Ensure upload directory exists
          await fs.mkdir(config.files.uploadPath, { recursive: true });
          cb(null, config.files.uploadPath);
        } catch (error) {
          logger.error('Failed to create upload directory:', error);
          cb(error);
        }
      },
      filename: (req, file, cb) => {
        // Generate unique filename with timestamp and random hash
        const uniqueSuffix = crypto.randomBytes(8).toString('hex');
        const timestamp = Date.now();
        const extension = path.extname(file.originalname);
        const filename = `cv_${timestamp}_${uniqueSuffix}${extension}`;
        cb(null, filename);
      }
    });
  }

  setupMulter() {
    // File filter for supported formats
    const fileFilter = (req, file, cb) => {
      try {
        // Check MIME type
        const supportedMimeTypes = [
          'application/pdf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'application/msword',
          'image/jpeg',
          'image/jpg', 
          'image/png',
          'text/plain'
        ];

        if (!supportedMimeTypes.includes(file.mimetype)) {
          const error = new Error(`Unsupported file type: ${file.mimetype}`);
          error.code = 'UNSUPPORTED_FILE_TYPE';
          return cb(error, false);
        }

        // Check file extension
        const supportedExtensions = config.files.supportedFormats.map(ext => `.${ext}`);
        const fileExtension = path.extname(file.originalname).toLowerCase();
        
        if (!supportedExtensions.includes(fileExtension)) {
          const error = new Error(`Unsupported file extension: ${fileExtension}`);
          error.code = 'UNSUPPORTED_FILE_EXTENSION';
          return cb(error, false);
        }

        logger.debug(`✅ File accepted: ${file.originalname}`, {
          mimetype: file.mimetype,
          extension: fileExtension
        });

        cb(null, true);
      } catch (error) {
        logger.error('File filter error:', error);
        cb(error, false);
      }
    };

    // Memory upload (primary method)
    this.memoryUpload = multer({
      storage: this.memoryStorage,
      fileFilter,
      limits: {
        fileSize: config.files.maxSize,
        files: 1, // Single file upload
        fields: 10, // Allow additional form fields
        fieldSize: 1024 * 1024 // 1MB for text fields
      }
    });

    // Disk upload (fallback for very large files)
    this.diskUpload = multer({
      storage: this.diskStorage,
      fileFilter,
      limits: {
        fileSize: config.files.maxSize,
        files: 1,
        fields: 10,
        fieldSize: 1024 * 1024
      }
    });
  }

  /**
   * Single file upload middleware (memory)
   */
  single(fieldName = 'cv') {
    return (req, res, next) => {
      const upload = this.memoryUpload.single(fieldName);
      
      upload(req, res, (error) => {
        if (error) {
          return this.handleUploadError(error, req, res, next);
        }

        // Add file metadata
        if (req.file) {
          req.file.uploadedAt = new Date().toISOString();
          req.file.uploadMethod = 'memory';
          
          logger.info(`📁 File uploaded successfully`, {
            filename: req.file.originalname,
            size: req.file.size,
            mimetype: req.file.mimetype,
            method: 'memory'
          });
        }

        next();
      });
    };
  }

  /**
   * Single file upload middleware (disk fallback)
   */
  singleDisk(fieldName = 'cv') {
    return (req, res, next) => {
      const upload = this.diskUpload.single(fieldName);
      
      upload(req, res, async (error) => {
        if (error) {
          return this.handleUploadError(error, req, res, next);
        }

        // Convert disk file to memory buffer for consistency
        if (req.file) {
          try {
            const buffer = await fs.readFile(req.file.path);
            req.file.buffer = buffer;
            req.file.uploadedAt = new Date().toISOString();
            req.file.uploadMethod = 'disk';
            
            // Schedule cleanup of temporary file
            this.scheduleCleanup(req.file.path);
            
            logger.info(`📁 File uploaded successfully (disk)`, {
              filename: req.file.originalname,
              size: req.file.size,
              mimetype: req.file.mimetype,
              path: req.file.path
            });
          } catch (readError) {
            logger.error('Failed to read uploaded file:', readError);
            return next(readError);
          }
        }

        next();
      });
    };
  }

  /**
   * Multiple files upload (for batch processing)
   */
  array(fieldName = 'cvs', maxCount = 5) {
    return (req, res, next) => {
      const upload = this.memoryUpload.array(fieldName, maxCount);
      
      upload(req, res, (error) => {
        if (error) {
          return this.handleUploadError(error, req, res, next);
        }

        // Add metadata to all files
        if (req.files && req.files.length > 0) {
          req.files.forEach(file => {
            file.uploadedAt = new Date().toISOString();
            file.uploadMethod = 'memory';
          });

          logger.info(`📁 Multiple files uploaded successfully`, {
            count: req.files.length,
            totalSize: req.files.reduce((sum, file) => sum + file.size, 0),
            filenames: req.files.map(file => file.originalname)
          });
        }

        next();
      });
    };
  }

  /**
   * Handle upload errors with proper categorization
   */
  handleUploadError(error, req, res, next) {
    logger.error('Upload error:', error);

    let statusCode = 400;
    let message = 'Upload failed';
    let code = 'UPLOAD_ERROR';

    switch (error.code) {
      case 'LIMIT_FILE_SIZE':
        statusCode = 413;
        message = `File too large. Maximum size is ${Math.round(config.files.maxSize / 1024 / 1024)}MB`;
        code = 'FILE_TOO_LARGE';
        break;

      case 'LIMIT_FILE_COUNT':
        statusCode = 400;
        message = 'Too many files uploaded';
        code = 'TOO_MANY_FILES';
        break;

      case 'LIMIT_UNEXPECTED_FILE':
        statusCode = 400;
        message = 'Unexpected file field';
        code = 'UNEXPECTED_FILE_FIELD';
        break;

      case 'UNSUPPORTED_FILE_TYPE':
      case 'UNSUPPORTED_FILE_EXTENSION':
        statusCode = 415;
        message = error.message;
        code = error.code;
        break;

      case 'ENOENT':
        statusCode = 500;
        message = 'Upload directory not accessible';
        code = 'DIRECTORY_ERROR';
        break;

      default:
        statusCode = 500;
        message = 'Internal upload error';
        code = 'INTERNAL_ERROR';
    }

    res.status(statusCode).json({
      error: code,
      message,
      details: {
        supportedFormats: config.files.supportedFormats,
        maxSize: `${Math.round(config.files.maxSize / 1024 / 1024)}MB`,
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Schedule cleanup of temporary files
   */
  scheduleCleanup(filePath) {
    setTimeout(async () => {
      try {
        await fs.unlink(filePath);
        logger.debug(`🗑️ Temporary file cleaned up: ${filePath}`);
      } catch (error) {
        if (error.code !== 'ENOENT') {
          logger.warn(`Failed to cleanup temporary file: ${filePath}`, error);
        }
      }
    }, config.files.cleanupInterval);
  }

  /**
   * Middleware to validate uploaded file content
   */
  validateFileContent() {
    return async (req, res, next) => {
      if (!req.file) {
        return res.status(400).json({
          error: 'NO_FILE_UPLOADED',
          message: 'No file was uploaded'
        });
      }

      try {
        const file = req.file;

        // Validate file is not empty
        if (file.size === 0) {
          return res.status(400).json({
            error: 'EMPTY_FILE',
            message: 'Uploaded file is empty'
          });
        }

        // Validate file buffer exists
        if (!file.buffer || file.buffer.length === 0) {
          return res.status(400).json({
            error: 'INVALID_FILE_BUFFER',
            message: 'File buffer is invalid or empty'
          });
        }

        // Check for potential malicious content (basic check)
        const suspiciousPatterns = [
          /<script/i,
          /javascript:/i,
          /vbscript:/i,
          /onload=/i,
          /onerror=/i
        ];

        const fileContent = file.buffer.toString('utf8', 0, Math.min(file.buffer.length, 1024));
        const isSuspicious = suspiciousPatterns.some(pattern => pattern.test(fileContent));

        if (isSuspicious) {
          logger.warn(`🚨 Suspicious file content detected`, {
            filename: file.originalname,
            mimetype: file.mimetype,
            ip: req.ip
          });

          return res.status(400).json({
            error: 'SUSPICIOUS_CONTENT',
            message: 'File contains potentially malicious content'
          });
        }

        // Validate file signature (magic numbers) for common types
        const isValidSignature = this.validateFileSignature(file.buffer, file.mimetype);
        if (!isValidSignature) {
          return res.status(400).json({
            error: 'INVALID_FILE_SIGNATURE',
            message: 'File signature does not match the declared type'
          });
        }

        logger.debug(`✅ File content validation passed`, {
          filename: file.originalname,
          size: file.size,
          mimetype: file.mimetype
        });

        next();
      } catch (error) {
        logger.error('File content validation error:', error);
        res.status(500).json({
          error: 'VALIDATION_ERROR',
          message: 'Failed to validate file content'
        });
      }
    };
  }

  /**
   * Validate file signature (magic numbers)
   */
  validateFileSignature(buffer, mimetype) {
    if (buffer.length < 4) return false;

    const signatures = {
      'application/pdf': [0x25, 0x50, 0x44, 0x46], // %PDF
      'image/jpeg': [0xFF, 0xD8, 0xFF],
      'image/png': [0x89, 0x50, 0x4E, 0x47],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [0x50, 0x4B], // ZIP (DOCX)
      'application/msword': [0xD0, 0xCF, 0x11, 0xE0] // DOC
    };

    const signature = signatures[mimetype];
    if (!signature) return true; // No signature check for this type

    for (let i = 0; i < signature.length; i++) {
      if (buffer[i] !== signature[i]) {
        return false;
      }
    }

    return true;
  }

  /**
   * Get upload statistics
   */
  getStats() {
    return {
      maxFileSize: config.files.maxSize,
      supportedFormats: config.files.supportedFormats,
      uploadPath: config.files.uploadPath,
      cleanupInterval: config.files.cleanupInterval
    };
  }
}

// Create singleton instance
const uploadMiddleware = new UploadMiddleware();

module.exports = uploadMiddleware;
