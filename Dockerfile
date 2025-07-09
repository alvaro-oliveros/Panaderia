# Multi-stage build for production efficiency
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 bakery && \
    mkdir -p /app && \
    chown -R bakery:bakery /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=bakery:bakery backend/app ./backend/app
COPY --chown=bakery:bakery frontend ./frontend
COPY --chown=bakery:bakery .env.example ./.env

# Switch to non-root user
USER bakery

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
# Start frontend server in background\n\
cd /app && python -m http.server 3000 --directory frontend &\n\
# Start backend server\n\
cd /app && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000' > start.sh && \
chmod +x start.sh

# Start command
CMD ["./start.sh"]