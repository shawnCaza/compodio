FROM node:23-slim

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Development mode
CMD ["npm", "run", "dev"]