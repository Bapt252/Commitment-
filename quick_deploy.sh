#!/bin/bash
# SuperSmartMatch V2 - Déploiement Express

echo "�� SuperSmartMatch V2 - Déploiement Express"
echo "==========================================="

# Vérifier que les parsers autonomes existent
if [ ! -f "fix-pdf-extraction.js" ] || [ ! -f "super-optimized-parser.js" ]; then
    echo "❌ Erreur: Parsers autonomes non trouvés"
    echo "   Veuillez placer fix-pdf-extraction.js et super-optimized-parser.js dans ce dossier"
    exit 1
fi

echo "✅ Parsers autonomes trouvés"

# 1. Créer la structure V2
echo "📁 Création de la structure V2..."
mkdir -p cv-parser-v2/parsers
mkdir -p job-parser-v2/parsers

# 2. Copier les parsers
echo "📄 Copie des parsers autonomes..."
cp fix-pdf-extraction.js cv-parser-v2/parsers/
cp super-optimized-parser.js cv-parser-v2/parsers/
cp *.sh cv-parser-v2/parsers/ 2>/dev/null || true

cp fix-pdf-extraction.js job-parser-v2/parsers/
cp super-optimized-parser.js job-parser-v2/parsers/
cp *.sh job-parser-v2/parsers/ 2>/dev/null || true

echo "✅ Parsers copiés"

# 3. Sauvegarder l'existant
echo "💾 Sauvegarde de l'architecture existante..."
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml docker-compose.v1.backup
    echo "✅ docker-compose.yml sauvegardé"
fi

# 4. Configuration .env
if [ ! -f ".env" ]; then
    echo "⚙️ Création de la configuration .env..."
    cat > .env << 'ENVEOF'
# SuperSmartMatch V2 Configuration
DB_USER=supersmatch
DB_PASSWORD=supersecret
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
REDIS_URL=redis://redis:6379
PARSER_MODE=autonomous
ENVEOF
    echo "✅ Configuration .env créée"
fi

echo ""
echo "🎯 PROCHAINES ÉTAPES MANUELLES:"
echo "1. Créer les Dockerfiles pour cv-parser-v2 et job-parser-v2"
echo "2. Créer le docker-compose.v2.yml"
echo "3. Construire et démarrer les services"
echo ""
echo "📋 Fichiers créés:"
echo "   • cv-parser-v2/parsers/ (avec tes scripts)"
echo "   • job-parser-v2/parsers/ (avec tes scripts)"
echo "   • .env (configuration)"
echo "   • docker-compose.v1.backup (sauvegarde)"

