# =======================
#  Base Image
# =======================
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies only once (cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment (faster installs)
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"


# =======================
#  Install Dependencies
# =======================
FROM base AS deps

# Copy only requirements to enable proper build caching
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# =======================
#  Development Image
# =======================
FROM deps AS dev

ENV PYTHONUNBUFFERED=1

# Install auto-reload and developer tools here
RUN pip install --no-cache-dir "uvicorn[standard]" watchdog

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Hot reload enabled for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# =======================
#  Production Image
# =======================
FROM deps AS prod

ENV PYTHONUNBUFFERED=1

# Copy only the app (cleaner, smaller)
COPY . .

EXPOSE 8000

# Production mode — no reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
