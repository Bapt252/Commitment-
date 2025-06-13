FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
# FIX OCR: Variable d'environnement Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    poppler-utils \
    tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng \
    imagemagick python3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/parsers /tmp/cv_parsing /tmp/job_parsing

COPY parsers/ /app/parsers/
RUN chmod +x /app/parsers/*.js

COPY app.py .

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5053/health || exit 1

EXPOSE 5053

CMD ["python", "app.py"]
