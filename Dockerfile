# ==============================================================================
# STAGE 1: Compilation Build Context Layer
# ==============================================================================
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS builder

ENV UV_COMPILE_BYTECODE=1
WORKDIR /app

# Install system compilation packages needed to safely build C extensions
RUN apk add --no-cache gcc musl-dev libffi-dev

# Mount the lockfile and build dependencies inside the explicit virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# ==============================================================================
# STAGE 2: Minimalist Production Execution Context Layer
# ==============================================================================
FROM python:3.11-alpine

WORKDIR /workspace

# Install runtime dependencies required for compiled modules on Alpine Linux
RUN apk add --no-cache libffi libgcc libstdc++ musl

# Copy the pre-compiled virtual environment layer from the builder stage
COPY --from=builder /app/.venv /workspace/.venv

# Copy internal application source files
COPY ./src /workspace/src

# Set explicit environment variables to ensure the shell maps the binaries accurately
ENV PATH="/workspace/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Invoke python explicitly to evaluate uvicorn under alpine's execution shell
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]