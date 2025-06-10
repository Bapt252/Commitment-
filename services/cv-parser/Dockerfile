# CV Parser Service Dockerfile
FROM node:18-alpine

# Install system dependencies for document processing
RUN apk add --no-cache \
    dumb-init \
    curl \
    poppler-utils \
    imagemagick \
    tesseract-ocr \
    tesseract-ocr-data-fra \
    tesseract-ocr-data-eng \
    python3 \
    py3-pip \
    make \
    g++

# Create app directory
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Create temp directories
RUN mkdir -p /tmp/uploads /var/log/app

# Change ownership
RUN chown -R nodejs:nodejs /app /tmp/uploads /var/log/app
USER nodejs

# Expose port
EXPOSE 5051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5051/health || exit 1

# Use dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]