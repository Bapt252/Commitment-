#!/bin/bash

# 🔧 Reconstruction Job Parser V2 - Fix définitif
# Résolution du bug AttributeError: 'Settings' object has no attribute 'REQUIRE_API_KEY'

echo "🔧 === RECONSTRUCTION JOB PARSER V2 - FIX DÉFINITIF ==="
echo "Résolution du bug REQUIRE_API_KEY..."
echo ""

# Fonction de logging
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

log "🛑 Arrêt du Job Parser défaillant..."

# Arrêt du conteneur problématique
JOB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i job | head -1)
if [ ! -z "$JOB_CONTAINER" ]; then
    log "Arrêt du conteneur: $JOB_CONTAINER"
    docker kill $JOB_CONTAINER
    docker rm $JOB_CONTAINER
else
    log "Aucun conteneur Job Parser à arrêter"
fi

# Nettoyage des processus sur 5053
log "🧹 Nettoyage du port 5053..."
pkill -f ".*5053.*" 2>/dev/null || log "Aucun processus sur 5053"

log "🏗️  Reconstruction du Job Parser V2..."

# Vérification de la présence du répertoire
if [ ! -d "job-parser-v2" ]; then
    log "❌ ERREUR: Répertoire job-parser-v2/ manquant"
    exit 1
fi

cd job-parser-v2

# Vérification des fichiers requis
MISSING_FILES=false

if [ ! -f "app.py" ]; then
    log "❌ ERREUR: app.py manquant"
    MISSING_FILES=true
fi

if [ ! -f "Dockerfile" ]; then
    log "❌ ERREUR: Dockerfile manquant"
    MISSING_FILES=true
fi

if [ ! -f "requirements.txt" ]; then
    log "❌ ERREUR: requirements.txt manquant"
    MISSING_FILES=true
fi

if [ "$MISSING_FILES" = true ]; then
    log "❌ ÉCHEC: Fichiers critiques manquants"
    exit 1
fi

log "✅ Tous les fichiers critiques présents"

# Construction de l'image Docker avec le bon code
log "🔨 Construction de l'image Docker (Flask)..."
docker build -t job-parser-v2-flask-fixed . --no-cache

if [ $? -ne 0 ]; then
    log "❌ ÉCHEC: Construction Docker échouée"
    exit 1
fi

log "✅ Image Docker construite avec succès"

# Démarrage du nouveau conteneur
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
CONTAINER_NAME="job-parser-v2-fixed-${TIMESTAMP}"

log "🚀 Démarrage du nouveau conteneur..."
docker run -d \
    -p 5053:5053 \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    job-parser-v2-flask-fixed

if [ $? -ne 0 ]; then
    log "❌ ÉCHEC: Démarrage du conteneur échoué"
    exit 1
fi

log "✅ Conteneur démarré: $CONTAINER_NAME"

# Attente du démarrage
log "⏳ Attente du démarrage (20 secondes)..."
sleep 20

# Tests de validation
log "🧪 Tests de validation..."

# Test health check
for i in {1..6}; do
    if curl -s http://localhost:5053/health > /dev/null; then
        log "✅ Job Parser V2 réparé avec succès !"
        HEALTH_RESPONSE=$(curl -s http://localhost:5053/health)
        echo "Réponse health: $HEALTH_RESPONSE"
        break
    else
        log "⏳ Tentative $i/6 - en attente..."
        sleep 5
    fi
done

# Test avec fichier PDF
if [ -f "/Users/baptistecomas/Desktop/FDPteste.pdf" ]; then
    log "📄 Test avec FDPteste.pdf..."
    
    PDF_RESULT=$(curl -s -X POST -F "file=@/Users/baptistecomas/Desktop/FDPteste.pdf" http://localhost:5053/api/parse-job/)
    
    if echo "$PDF_RESULT" | grep -q '"status":"success"'; then
        log "🎉 SUCCÈS ! FDPteste.pdf parsé avec succès"
        
        echo ""
        echo "🚀 === TEST COMPLET POSSIBLE ==="
        echo ""
        echo "Vous pouvez maintenant tester le matching Enhanced V2.1 complet :"
        echo ""
        echo "curl -X POST \\"
        echo "  -F \"cv_file=@/Users/baptistecomas/Desktop/BATU Sam.pdf\" \\"
        echo "  -F \"job_file=@/Users/baptistecomas/Desktop/FDPteste.pdf\" \\"
        echo "  http://localhost:5055/api/matching/files"
        echo ""
        echo "OU avec le script Python :"
        echo "python test_matching_system.py --cv \"/Users/baptistecomas/Desktop/BATU Sam.pdf\" --job \"/Users/baptistecomas/Desktop/FDPteste.pdf\""
        
    else
        log "❌ Échec du parsing PDF"
        echo "Réponse: $PDF_RESULT"
        
        # Affichage des logs pour diagnostic
        log "📋 Logs du nouveau conteneur:"
        docker logs --tail 20 $CONTAINER_NAME
    fi
else
    log "⚠️  Fichier FDPteste.pdf non trouvé pour le test"
fi

cd ..

# État final
echo ""
echo "📊 === ÉTAT FINAL DES SERVICES ==="

echo "CV Parser V2 (5051):"
curl -s http://localhost:5051/health > /dev/null && echo " ✅ Actif" || echo " ❌ Inactif"

echo "Job Parser V2 (5053):"
curl -s http://localhost:5053/health > /dev/null && echo " ✅ Actif" || echo " ❌ Inactif"

echo "Enhanced API V2.1 (5055):"
curl -s http://localhost:5055/health > /dev/null && echo " ✅ Actif" || echo " ❌ Inactif"

echo ""
log "🏁 Reconstruction Job Parser V2 terminée"

# Conteneurs actifs
echo ""
echo "📋 Conteneurs Docker actifs:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(5051|5053|5055|job-parser|cv-parser)" || echo "Aucun conteneur trouvé"

echo ""
echo "🎯 Le Job Parser V2 devrait maintenant fonctionner avec le code Flask correct !"
