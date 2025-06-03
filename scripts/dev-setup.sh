#!/bin/bash
# Setup de l'environnement de développement
set -e

echo "🚀 Configuration de l'environnement de développement..."

# Vérification des prérequis
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    echo "Installez Docker depuis https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    echo "Installez Docker Compose depuis https://docs.docker.com/compose/install/"
    exit 1
fi

# Installation de Poetry si pas déjà installé
if ! command -v poetry &> /dev/null; then
    echo "📦 Installation de Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Configuration de Poetry
echo "⚙️  Configuration de Poetry..."
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true

# Installation des dépendances
echo "📚 Installation des dépendances..."
poetry install

# Configuration des pre-commit hooks
echo "🔧 Configuration des pre-commit hooks..."
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg

# Création des répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p {\
    logs,\
    monitoring/{prometheus/{rules,data},grafana/{dashboards,provisioning/{datasources,dashboards}}},\
    notebooks,\
    data,\
    tests/{unit,integration,performance},\
    dev-tools/jupyter,\
    shared/{middleware,metrics,logging}\
}

# Copie des fichiers de configuration s'ils n'existent pas
if [ ! -f .env ]; then
    echo "📄 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  N'oubliez pas de configurer votre clé API OpenAI dans .env"
fi

# Création du fichier gitignore pour les logs et données
echo "📝 Mise à jour du .gitignore..."
cat >> .gitignore << 'EOF'

# Development environment
logs/
notebooks/.ipynb_checkpoints/
data/
*.prof
bandit-report.json
coverage.xml
htmlcov/
.coverage
.pytest_cache/

# Poetry
.venv/
poetry.lock

# Monitoring data
monitoring/prometheus/data/
monitoring/grafana/data/
EOF

echo "✅ Environnement de développement configuré avec succès !"
echo ""
echo "Prochaines étapes :"
echo "1. Configurez votre clé API OpenAI dans le fichier .env"
echo "2. Utilisez 'make help' pour voir les commandes disponibles"
echo "3. Démarrez l'environnement avec 'make dev-up'"
echo "4. Accédez à Jupyter Lab sur http://localhost:8888"
echo "5. Accédez à Grafana sur http://localhost:3001"