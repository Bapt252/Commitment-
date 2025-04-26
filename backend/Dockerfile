# Étape de build
FROM python:3.11-slim as builder

# Dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire des wheels
WORKDIR /wheels

# Copier uniquement le fichier requirements pour le cache
COPY requirements.txt .

# Compiler les wheels
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Image finale
FROM python:3.11-slim

# Dépendances runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copier les wheels depuis le builder
COPY --from=builder /wheels /wheels

# Installer les dépendances depuis les wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl \
    && rm -rf /wheels

# Assurer que OpenAI est en version 0.28.1
RUN pip uninstall -y openai && pip install openai==0.28.1

# Forcer la version compatible de huggingface_hub
RUN pip uninstall -y huggingface_hub && pip install huggingface_hub==0.16.4

# Installer les modèles spaCy
COPY setup_spacy_models.py /tmp/
RUN python /tmp/setup_spacy_models.py && rm /tmp/setup_spacy_models.py

# Précharger les modèles sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print('Modèle sentence-transformers préchargé')"

# Créer l'utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=appuser:appuser . .

# Passer à l'utilisateur non-root
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Port exposé
EXPOSE 5000

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]