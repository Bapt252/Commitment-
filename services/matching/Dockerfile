# Matching Service Dockerfile
FROM node:18-alpine

# Install Python for ML libraries
RUN apk add --no-cache \
    dumb-init \
    curl \
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
RUN npm install --production && npm cache clean --force

# Copy source code
COPY . .

# Create directories
RUN mkdir -p /var/models /var/log/app

# Change ownership
RUN chown -R nodejs:nodejs /app /var/models /var/log/app
USER nodejs

# Expose port
EXPOSE 5052

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5052/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]