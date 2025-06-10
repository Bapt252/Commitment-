FROM node:18-alpine

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S apigateway -u 1001

# Copy app source
COPY --chown=apigateway:nodejs . .

# Create logs directory
RUN mkdir -p /var/log/app && chown apigateway:nodejs /var/log/app

# Switch to non-root user
USER apigateway

# Expose port
EXPOSE 5050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node healthcheck.js

CMD ["npm", "start"]
