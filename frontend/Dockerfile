FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci

# Copy the rest of the app
COPY . .

# Build the app for production
RUN npm run build

# Expose the port
EXPOSE 3000

# Start the app
CMD ["npm", "run", "dev"]
