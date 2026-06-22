# ==========================================
# Stage 1: Build & Compilation Environment
# ==========================================
FROM python:3.12-slim AS builder

# Set build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy package configurations
COPY pyproject.toml uv.lock ./

# Create virtual environment and synchronize dependencies inside it
RUN uv venv $VIRTUAL_ENV && \
    uv pip install --no-cache -r pyproject.toml

# ==========================================
# Stage 2: Final Production Runtime
# ==========================================
FROM python:3.12-slim AS runtime

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy compiled virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy project source trees
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create a non-privileged system user for container security hardening
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -M appuser && \
    chown -R appuser:appgroup /app

# Run container process as non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Executed command by default
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
