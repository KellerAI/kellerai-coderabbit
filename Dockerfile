# KellerAI CodeRabbit Integration - Production Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files
WORKDIR /build
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy source code
COPY quality_checks/ quality_checks/
COPY mcp_servers/ mcp_servers/

# Install the package
RUN pip install --no-deps .

# Stage 2: Production
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    KELLERAI_REPO_ROOT=/app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash kellerai && \
    mkdir -p /app && \
    chown -R kellerai:kellerai /app

# Copy virtual environment from builder
COPY --from=builder --chown=kellerai:kellerai /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=kellerai:kellerai .coderabbit.yaml .
COPY --chown=kellerai:kellerai .mcp.json .
COPY --chown=kellerai:kellerai docs/ docs/
COPY --chown=kellerai:kellerai templates/ templates/
COPY --chown=kellerai:kellerai knowledge-base/ knowledge-base/

# Copy MCP server files
COPY --chown=kellerai:kellerai mcp_servers/kellerai-standards/ mcp_servers/kellerai-standards/

# Switch to non-root user
USER kellerai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import quality_checks; print('OK')" || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "quality_checks.quality_orchestrator"]

# Labels
LABEL maintainer="KellerAI Engineering <engineering@kellerai.com>" \
      version="1.0.0" \
      description="KellerAI CodeRabbit Integration" \
      org.opencontainers.image.source="https://github.com/kellerai/coderabbit"
