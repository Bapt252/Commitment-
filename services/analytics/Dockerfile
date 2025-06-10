# Analytics Service Dockerfile
FROM node:18-alpine

RUN apk add --no-cache dumb-init curl

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

# Create directories
RUN mkdir -p /var/log/app

# Change ownership
RUN chown -R nodejs:nodejs /app /var/log/app
USER nodejs

# Expose port
EXPOSE 5056

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5056/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]