# Étape de build
FROM python:3.11-slim as builder

# Dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire des wheels
WORKDIR /wheels

# Copier uniquement le fichier requirements pour le cache
COPY requirements.txt .

# Installer pydantic-settings
RUN pip install --no-cache-dir pydantic-settings>=2.0.0

# Compiler les wheels
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Image finale
FROM python:3.11-slim

# Dépendances runtime pour traitement de documents
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    curl \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    antiword \
    unrtf \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copier les wheels depuis le builder
COPY --from=builder /wheels /wheels

# Installer les dépendances depuis les wheels et installer pydantic-settings
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl \
    && pip install --no-cache-dir pydantic-settings>=2.0.0 \
    && rm -rf /wheels

# Créer l'utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer les répertoires nécessaires avec les permissions correctes
RUN mkdir -p /app/logs /app/temp && \
    chmod 777 /app/logs && \
    chmod 777 /app/temp && \
    chown -R appuser:appuser /app

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=appuser:appuser . .

# Rendre les scripts exécutables
RUN chmod +x entrypoint.sh
RUN chmod +x fix-indentation.sh

# Passer à l'utilisateur non-root
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Port exposé
EXPOSE 5000

# Commande par défaut avec entrypoint comme shell script
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "main.py"]
