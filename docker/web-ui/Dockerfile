# AI Video GPU - Web UI Container
# React/Vue.js frontend with real-time monitoring

FROM node:18-alpine

LABEL maintainer="AI-Empower-Cloud"
LABEL description="Web UI - React/Vue.js Frontend with Real-time Monitoring"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl

# Copy package files first for better caching
COPY docker/web-ui/package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Install development tools globally
RUN npm install -g \
    @vue/cli \
    create-react-app \
    vite \
    serve

# Copy application code
COPY docker/web-ui/src/ ./src/
COPY docker/web-ui/public/ ./public/
COPY docker/web-ui/index.html ./
COPY docker/web-ui/vite.config.js ./
COPY docker/web-ui/tailwind.config.js ./
COPY docker/web-ui/postcss.config.js ./

# Build the application
RUN npm run build

# Create nginx configuration for serving
RUN echo 'server {\n\
    listen 8005;\n\
    root /app/dist;\n\
    index index.html;\n\
    \n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    location /api/ {\n\
        proxy_pass http://api-backend:8006/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
    \n\
    location /ws {\n\
        proxy_pass http://api-backend:8006/ws;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Install nginx for production serving
RUN apk add --no-cache nginx

# Create directories
RUN mkdir -p /var/log/nginx /var/lib/nginx/tmp /run/nginx

# Copy startup script
COPY docker/web-ui/start.sh ./
RUN chmod +x start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Expose port
EXPOSE 8005

# Start the web UI
CMD ["./start.sh"]
