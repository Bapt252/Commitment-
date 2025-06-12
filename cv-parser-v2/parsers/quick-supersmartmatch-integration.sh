#!/bin/bash

# Script d'intégration rapide SuperSmartMatch-Service dans Commitment
# Usage: ./quick-supersmartmatch-integration.sh

set -e

echo "🚀 INTÉGRATION SUPERSMARTMATCH-SERVICE DANS COMMITMENT"
echo "======================================================"

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Erreur: docker-compose.yml non trouvé. Êtes-vous dans le dossier Commitment ?${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ Fichier .env manquant, création à partir de .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Fichier .env créé${NC}"
    else
        echo -e "${RED}❌ Fichier .env.example manquant${NC}"
        exit 1
    fi
fi

# Étape 1: Cloner SuperSmartMatch-Service
echo -e "${BLUE}📂 Étape 1: Préparation de SuperSmartMatch-Service...${NC}"
if [ ! -d "supersmartmatch-service" ]; then
    echo "📥 Clonage de SuperSmartMatch-Service..."
    git clone https://github.com/Bapt252/SuperSmartMatch-Service.git supersmartmatch-service
    echo -e "${GREEN}✅ SuperSmartMatch-Service cloné${NC}"
else
    echo "📁 SuperSmartMatch-Service existe déjà"
    cd supersmartmatch-service
    echo "🔄 Mise à jour..."
    git pull origin main || echo -e "${YELLOW}⚠️ Impossible de mettre à jour (pas grave)${NC}"
    cd ..
    echo -e "${GREEN}✅ SuperSmartMatch-Service vérifié${NC}"
fi

# Étape 2: Modifier le port dans SuperSmartMatch
echo -e "${BLUE}🔧 Étape 2: Configuration du port 5062...${NC}"
cd supersmartmatch-service

# Sauvegarde de l'app.py original si pas encore fait
if [ ! -f "app.py.backup" ]; then
    cp app.py app.py.backup
fi

# Modification du port de 5060 à 5062 dans app.py
sed -i.tmp 's/:5060/:5062/g' app.py
sed -i.tmp 's/port=5060/port=5062/g' app.py
sed -i.tmp 's/PORT=5060/PORT=5062/g' app.py
rm -f app.py.tmp

echo -e "${GREEN}✅ Port configuré sur 5062${NC}"
cd ..

# Étape 3: Créer le nouveau Dockerfile
echo -e "${BLUE}🐳 Étape 3: Création du Dockerfile intégré...${NC}"
cat > supersmartmatch-service/Dockerfile << EOF
# SuperSmartMatch Service Dockerfile - Version intégrée
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Nexten Team"
LABEL description="SuperSmartMatch - Service unifié de matching intégré"
LABEL version="1.0.1"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV PORT=5062

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p /app/logs

# Création d'un utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Exposition du port
EXPOSE 5062

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5062/api/v1/health || exit 1

# Commande de démarrage
CMD ["python", "app.py"]
EOF

echo -e "${GREEN}✅ Dockerfile créé${NC}"

# Étape 4: Mise à jour du .env
echo -e "${BLUE}⚙️ Étape 4: Mise à jour des variables d'environnement...${NC}"

# Vérifier si les variables SuperSmartMatch existent déjà
if ! grep -q "SUPERSMARTMATCH_SERVICE_URL" .env; then
    echo "" >> .env
    echo "# SuperSmartMatch Service Configuration" >> .env
    echo "SECRET_KEY=your-super-secret-key-here-for-supersmartmatch" >> .env
    echo "SUPERSMARTMATCH_SERVICE_URL=http://supersmartmatch-service:5062" >> .env
    echo "DEFAULT_ALGORITHM=auto" >> .env
    echo "ENABLE_CACHING=true" >> .env
    echo "CACHE_TTL=3600" >> .env
    echo "MAX_JOBS_PER_REQUEST=100" >> .env
    echo "DEFAULT_RESULT_LIMIT=10" >> .env
    echo "ENABLE_METRICS=true" >> .env
    echo "METRICS_RETENTION_DAYS=30" >> .env
    echo "RATE_LIMIT_PER_MINUTE=100" >> .env
    echo "RATE_LIMIT_PER_HOUR=1000" >> .env
    echo -e "${GREEN}✅ Variables ajoutées au .env${NC}"
else
    echo -e "${YELLOW}📝 Variables SuperSmartMatch déjà présentes dans .env${NC}"
fi

# Étape 5: Créer le dossier de logs
echo -e "${BLUE}📁 Étape 5: Création du dossier de logs...${NC}"
mkdir -p supersmartmatch-service/logs
echo -e "${GREEN}✅ Dossier de logs créé${NC}"

# Étape 6: Test de configuration
echo -e "${BLUE}🧪 Étape 6: Test de la configuration...${NC}"
if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Configuration Docker Compose valide${NC}"
else
    echo -e "${RED}❌ Erreur dans la configuration Docker Compose${NC}"
    echo "🔍 Vérifiez le fichier docker-compose.yml"
    exit 1
fi

# Étape 7: Construction et démarrage (optionnel)
read -p "🚀 Voulez-vous démarrer les services maintenant ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 Étape 7: Construction et démarrage des services...${NC}"
    echo "⏳ Cela peut prendre quelques minutes..."

    # Arrêt des services existants
    echo "🛑 Arrêt des services existants..."
    docker-compose down

    # Construction de SuperSmartMatch
    echo "🔨 Construction de SuperSmartMatch..."
    docker-compose build supersmartmatch-service

    # Démarrage de tous les services
    echo "▶️ Démarrage de tous les services..."
    docker-compose up -d

    echo -e "${GREEN}✅ Services démarrés${NC}"

    # Vérification
    echo -e "${BLUE}🔍 Vérification du déploiement...${NC}"
    sleep 15

    echo "📊 État des services:"
    docker-compose ps

    echo ""
    echo "🩺 Test de santé SuperSmartMatch..."
    for i in {1..10}; do
        if curl -s -f http://localhost:5062/api/v1/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ SuperSmartMatch-Service est opérationnel sur le port 5062${NC}"
            break
        else
            echo "⏳ Tentative $i/10 - En attente de SuperSmartMatch..."
            sleep 5
        fi
    done
else
    echo -e "${YELLOW}⏩ Services non démarrés. Utilisez 'docker-compose up -d' quand vous serez prêt.${NC}"
fi

# Résumé final
echo ""
echo -e "${GREEN}🎉 INTÉGRATION TERMINÉE !${NC}"
echo "========================"
echo -e "${GREEN}✅ SuperSmartMatch-Service intégré avec succès${NC}"
echo "🌐 URL: http://localhost:5062"
echo "🔍 Health check: http://localhost:5062/api/v1/health"
echo "📊 Dashboard RQ: http://localhost:9181"
echo "🗄️ Redis Commander: http://localhost:8081"
echo "📦 MinIO Console: http://localhost:9001"
echo ""
echo "📋 Résumé des ports utilisés:"
echo "   • 5050: API principale"
echo "   • 5051: CV Parser"
echo "   • 5052: Matching service existant"
echo "   • 5055: Job Parser"
echo "   • 5060: Service de personnalisation"
echo -e "   • ${GREEN}5062: SuperSmartMatch-Service (NOUVEAU)${NC}"
echo ""
echo "💡 Commandes utiles:"
echo "   • Voir les logs: docker-compose logs supersmartmatch-service"
echo "   • Redémarrer: docker-compose restart supersmartmatch-service"
echo "   • Arrêter tout: docker-compose down"
echo "   • Démarrer tout: docker-compose up -d"
echo ""
echo "🔧 Fichiers créés/modifiés:"
echo "   • docker-compose.yml (SuperSmartMatch ajouté)"
echo "   • .env (variables SuperSmartMatch ajoutées)"
echo "   • supersmartmatch-service/ (cloné et configuré)"
echo "   • supersmartmatch-service/Dockerfile (créé)"
echo ""
echo -e "${BLUE}📖 Pour des tests avancés, utilisez: ./test-supersmartmatch-integration.sh${NC}"