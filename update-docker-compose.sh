#!/bin/bash

# Script pour intégrer SuperSmartMatch dans le docker-compose.yml principal
# Auteur: Nexten Team

echo "🔧 Intégration de SuperSmartMatch dans l'infrastructure Nexten"
echo "================================================================"

# Vérification que nous sommes dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Fichier docker-compose.yml non trouvé."
    echo "   Veuillez exécuter ce script depuis la racine du projet Nexten."
    exit 1
fi

echo "✅ Répertoire de projet Nexten détecté"

# Sauvegarde du docker-compose.yml existant
echo "💾 Sauvegarde du docker-compose.yml existant..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
echo "   Sauvegarde créée: docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)"

# Vérification si SuperSmartMatch est déjà intégré
if grep -q "super-smart-match" docker-compose.yml; then
    echo "⚠️  SuperSmartMatch semble déjà intégré dans docker-compose.yml"
    echo "   Voulez-vous continuer et écraser la configuration? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Intégration annulée"
        exit 0
    fi
fi

# Intégration de SuperSmartMatch
echo "🚀 Ajout de SuperSmartMatch au docker-compose.yml..."

# Créer un fichier temporaire avec la nouvelle configuration
cat > temp_supersmartmatch.yml << 'EOF'

  # SuperSmartMatch - Service unifié de matching intelligent
  super-smart-match:
    build:
      context: ./super-smart-match-service
      dockerfile: Dockerfile
    container_name: nexten-super-smart-match
    ports:
      - "5070:5070"
    environment:
      - ENVIRONMENT=production
      - PORT=5070
      - HOST=0.0.0.0
      - LOG_LEVEL=INFO
      # Connexion aux services existants
      - REDIS_URL=redis://nexten-redis:6379/0
      - DATABASE_URL=postgresql://nexten_user:nexten_password@nexten-postgres:5432/nexten_db
      # APIs des autres services pour fallback
      - CV_PARSER_URL=http://nexten-cv-parser:5051
      - JOB_PARSER_URL=http://nexten-job-parser:5055  
      - MATCHING_SERVICE_URL=http://nexten-matching:5052
      - PERSONALIZATION_URL=http://nexten-personalization:5060
    volumes:
      # Logs partagés
      - ./logs:/app/logs
      # Accès aux algorithmes du répertoire parent
      - ./matching_engine.py:/app/matching_engine.py:ro
      - ./enhanced_matching_engine.py:/app/enhanced_matching_engine.py:ro
      - ./my_matching_engine.py:/app/my_matching_engine.py:ro
      - ./compare_algorithms.py:/app/compare_algorithms.py:ro
    networks:
      - nexten-network
    depends_on:
      - nexten-redis
      - nexten-postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5070/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "com.nexten.service=super-smart-match"
      - "com.nexten.version=1.0.0"
      - "com.nexten.description=Service unifié de matching intelligent"
EOF

# Insertion dans le docker-compose.yml après les autres services
if grep -q "services:" docker-compose.yml; then
    # Trouve la ligne après le dernier service et insère SuperSmartMatch
    awk '
    /^services:/ { in_services=1; print; next }
    in_services && /^[[:space:]]*[a-zA-Z0-9_-]+:/ { last_service_line=NR }
    { lines[NR] = $0 }
    END {
        for (i=1; i<=last_service_line; i++) print lines[i]
        while ((getline line < "temp_supersmartmatch.yml") > 0) print line
        for (i=last_service_line+1; i<=NR; i++) print lines[i]
    }
    ' docker-compose.yml > docker-compose.yml.new
    
    mv docker-compose.yml.new docker-compose.yml
    rm temp_supersmartmatch.yml
    
    echo "✅ SuperSmartMatch ajouté avec succès au docker-compose.yml"
else
    echo "❌ Structure docker-compose.yml non reconnue"
    echo "   Veuillez ajouter manuellement la configuration SuperSmartMatch"
    cat temp_supersmartmatch.yml
    rm temp_supersmartmatch.yml
    exit 1
fi

# Mise à jour du start-all-services.sh si il existe
if [ -f "start-all-services.sh" ]; then
    echo "🔧 Mise à jour de start-all-services.sh..."
    
    # Ajouter SuperSmartMatch à la liste des services si pas déjà présent
    if ! grep -q "super-smart-match" start-all-services.sh; then
        # Chercher une ligne avec docker-compose up et ajouter le service
        sed -i 's/docker-compose up -d/docker-compose up -d super-smart-match/g' start-all-services.sh
        echo "   ✅ start-all-services.sh mis à jour"
    else
        echo "   ℹ️  start-all-services.sh déjà à jour"
    fi
fi

# Mise à jour du README principal
echo "📚 Mise à jour du README principal..."
if [ -f "README.md" ]; then
    # Ajouter SuperSmartMatch à la liste des services
    if ! grep -q "SuperSmartMatch" README.md; then
        # Chercher la section des services et ajouter SuperSmartMatch
        sed -i '/Service de matching.*5052/a\- **SuperSmartMatch (Service unifié)**: http://localhost:5070' README.md
        echo "   ✅ README.md mis à jour avec SuperSmartMatch"
    else
        echo "   ℹ️  SuperSmartMatch déjà mentionné dans README.md"
    fi
fi

echo ""
echo "🎉 Intégration terminée avec succès !"
echo "================================================================"
echo "📋 Prochaines étapes:"
echo "   1. 🚀 Démarrer tous les services: ./start-all-services.sh"
echo "   2. 🧪 Tester SuperSmartMatch: cd super-smart-match-service && ./test-supersmartmatch.sh"
echo "   3. 🌐 Accéder à l'API: http://localhost:5070"
echo "   4. 📖 Documentation: http://localhost:5070/docs"
echo ""
echo "🔗 Services disponibles après démarrage:"
echo "   - API SuperSmartMatch: http://localhost:5070"
echo "   - Health Check: http://localhost:5070/health"
echo "   - Documentation: http://localhost:5070/docs"
echo "   - Algorithmes: http://localhost:5070/algorithms"
echo ""
echo "💡 Pour modifier la configuration front-end:"
echo "   Remplacez les appels aux services individuels par:"
echo "   fetch('http://localhost:5070/api/v1/match', { method: 'POST', ... })"
echo ""
