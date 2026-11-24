# Minimal Python runtime for Voice & Skill Card Prototype
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install required system fonts for Devanagari and Kannada rendering + curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    fonts-lohit-deva \
    fonts-lohit-knda \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements_voice_card.txt .
RUN pip install --no-cache-dir -r requirements_voice_card.txt

# Copy application source files
COPY skill_card.py voice_service.py extras_helper.py myscheme_links.json ./

# Ensure cache and output directories exist
RUN mkdir -p /app/generated_cards /app/audio_cache

# Expose standard container port for cloud hosting
EXPOSE 8000

# Default entrypoint (teammates can override with their FastAPI/Flask server command)
CMD ["python", "-c", "import skill_card, voice_service, extras_helper; print('Voice & Skill Card Container Ready.')"]
