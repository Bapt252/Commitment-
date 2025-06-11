#!/bin/bash
# 🚀 CV Parser Ultra v2.0 - PROMPT 2 Entrypoint
# Script d'initialisation optimisé pour streaming temps réel

set -e

echo "🚀 Initialisation CV Parser Ultra v2.0..."

# Vérification des variables d'environnement essentielles
if [ -z "$REDIS_URL" ]; then
    echo "⚠️  REDIS_URL non défini, utilisation de la valeur par défaut"
    export REDIS_URL="redis://localhost:6379"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY non défini - fonctionnalités IA limitées"
fi

# Création des répertoires nécessaires
mkdir -p /tmp/uploads /var/log/app /var/cache/cv-parser
chmod 755 /tmp/uploads /var/log/app /var/cache/cv-parser

echo "📁 Répertoires créés:"
echo "   - /tmp/uploads (uploads temporaires)"
echo "   - /var/log/app (logs application)"
echo "   - /var/cache/cv-parser (cache local)"

# Vérification de la connexion Redis
echo "🔗 Vérification de la connexion Redis..."
python3 -c "
import asyncio
import aioredis
import sys

async def test_redis():
    try:
        redis = await aioredis.from_url('$REDIS_URL')
        await redis.ping()
        await redis.close()
        print('✅ Redis connecté avec succès')
        return True
    except Exception as e:
        print(f'❌ Erreur Redis: {e}')
        return False

result = asyncio.run(test_redis())
sys.exit(0 if result else 1)
" || {
    echo "❌ Impossible de se connecter à Redis"
    echo "🔄 Tentative de démarrage sans cache..."
    export REDIS_ENABLED=false
}

# Test OCR (Tesseract)
echo "🖼️  Vérification OCR..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR disponible"
    tesseract --version | head -1
else
    echo "❌ Tesseract OCR non disponible"
fi

# Installation des modèles spaCy si nécessaire
echo "🧠 Vérification modèles NLP..."
python3 -c "
import spacy
try:
    nlp = spacy.load('fr_core_news_sm')
    print('✅ Modèle français spaCy chargé')
except OSError:
    print('⚠️  Modèle français spaCy non trouvé, téléchargement...')
    import subprocess
    subprocess.run(['python3', '-m', 'spacy', 'download', 'fr_core_news_sm'])
    print('✅ Modèle français spaCy installé')
except Exception as e:
    print(f'❌ Erreur modèle spaCy: {e}')
" || echo "⚠️  Fonctionnalités NLP limitées"

# Mise à jour des permissions
echo "🔒 Configuration des permissions..."
chown -R app:app /tmp/uploads /var/log/app /var/cache/cv-parser 2>/dev/null || true

# Configuration du logging
export PYTHONUNBUFFERED=1
export LOG_LEVEL=${LOG_LEVEL:-info}

echo "📊 Configuration des métriques Prometheus..."
export PROMETHEUS_METRICS_PORT=${PROMETHEUS_METRICS_PORT:-9090}

# Nettoyage des fichiers temporaires anciens
echo "🧹 Nettoyage des fichiers temporaires..."
find /tmp/uploads -name "*.tmp" -mtime +1 -delete 2>/dev/null || true
find /var/cache/cv-parser -name "*.cache" -mtime +7 -delete 2>/dev/null || true

echo "✅ Initialisation terminée!"
echo ""
echo "🚀 Démarrage CV Parser Ultra v2.0..."
echo "   📋 Mode: ${NODE_ENV:-production}"
echo "   🔌 Port: ${PORT:-5051}"
echo "   📊 Metrics: Port ${PROMETHEUS_METRICS_PORT:-9090}"
echo "   💾 Cache Redis: ${REDIS_ENABLED:-true}"
echo "   🧠 IA/OCR: $([ -n "$OPENAI_API_KEY" ] && echo "Activé" || echo "Limité")"
echo ""

# Démarrage de l'application
exec "$@"
