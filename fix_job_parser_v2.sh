#!/bin/bash

# 🔧 Diagnostic et Résolution Job Parser V2 - Erreur 500
# Fix pour le Job Parser sur port 5053

echo "🔧 === DIAGNOSTIC JOB PARSER V2 - PORT 5053 ==="
echo "Résolution de l'erreur 500 lors du parsing des fichiers PDF..."
echo ""

# Fonction de logging
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# 1. Diagnostic de l'état actuel
log "🔍 État actuel du Job Parser V2..."

# Test health check
HEALTH_CHECK=$(curl -s http://localhost:5053/health)
if [ $? -eq 0 ]; then
    log "✅ Job Parser V2 répond au health check"
    echo "Réponse: $HEALTH_CHECK"
else
    log "❌ Job Parser V2 ne répond pas"
fi

echo ""

# 2. Vérification des conteneurs Docker
log "🐳 Conteneurs Docker Job Parser..."
JOB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i job | head -1)

if [ ! -z "$JOB_CONTAINER" ]; then
    log "✅ Conteneur trouvé: $JOB_CONTAINER"
    
    # Informations sur le conteneur
    echo "Status: $(docker ps --format "{{.Status}}" --filter "name=$JOB_CONTAINER")"
    echo "Ports: $(docker ps --format "{{.Ports}}" --filter "name=$JOB_CONTAINER")"
    
    # Logs récents du conteneur
    log "📋 Logs récents du Job Parser..."
    docker logs --tail 20 $JOB_CONTAINER
    
else
    log "❌ Aucun conteneur Job Parser trouvé"
fi

echo ""

# 3. Test avec un fichier simple
log "🧪 Test avec fichier exemple..."

# Créer un PDF de test simple si disponible
if [ -f "/Users/baptistecomas/Desktop/FDPteste.pdf" ]; then
    log "Test avec FDPteste.pdf..."
    JOB_RESULT=$(curl -s -X POST -F "file=@/Users/baptistecomas/Desktop/FDPteste.pdf" http://localhost:5053/api/parse-job/)
    echo "Réponse Job Parser:"
    echo "$JOB_RESULT" | jq . 2>/dev/null || echo "$JOB_RESULT"
fi

echo ""

# 4. Solutions proposées
echo "🛠️  === SOLUTIONS PROPOSÉES ==="
echo ""

echo "1. 🔄 Redémarrage du conteneur Job Parser:"
echo "   docker restart $JOB_CONTAINER"
echo ""

echo "2. 🔨 Reconstruction du Job Parser:"
echo "   cd job-parser-v2"
echo "   docker build -t job-parser-v2-fixed ."
echo "   docker run -d -p 5053:5053 --name job-parser-v2-fixed job-parser-v2-fixed"
echo ""

echo "3. 🚨 Reset complet Job Parser:"
echo "   docker kill \$(docker ps -q --filter 'publish=5053')"
echo "   docker rm \$(docker ps -aq --filter 'publish=5053')"
echo ""

echo "4. 🐍 Démarrage direct Python:"
echo "   cd job-parser-v2"
echo "   python app.py"
echo ""

# 5. Auto-fix option
read -p "🤖 Voulez-vous que je tente une résolution automatique ? (y/n): " auto_fix

if [ "$auto_fix" = "y" ] || [ "$auto_fix" = "Y" ]; then
    log "🔄 Début de la résolution automatique..."
    
    if [ ! -z "$JOB_CONTAINER" ]; then
        log "Redémarrage du conteneur Job Parser..."
        docker restart $JOB_CONTAINER
        
        log "Attente du redémarrage (15 secondes)..."
        sleep 15
        
        # Test après redémarrage
        log "Test après redémarrage..."
        if curl -s http://localhost:5053/health > /dev/null; then
            log "✅ Job Parser redémarré avec succès"
            
            # Test avec le fichier
            if [ -f "/Users/baptistecomas/Desktop/FDPteste.pdf" ]; then
                log "Test du fichier FDPteste.pdf..."
                TEST_RESULT=$(curl -s -X POST -F "file=@/Users/baptistecomas/Desktop/FDPteste.pdf" http://localhost:5053/api/parse-job/)
                
                if echo "$TEST_RESULT" | grep -q '"status":"success"'; then
                    log "🎉 SUCCÈS ! Job Parser fonctionne maintenant"
                    echo ""
                    echo "🚀 Vous pouvez maintenant tester le matching complet:"
                    echo "curl -X POST \\"
                    echo "  -F \"cv_file=@/Users/baptistecomas/Desktop/BATU Sam.pdf\" \\"
                    echo "  -F \"job_file=@/Users/baptistecomas/Desktop/FDPteste.pdf\" \\"
                    echo "  http://localhost:5055/api/matching/files"
                else
                    log "❌ Problème persiste après redémarrage"
                    echo "Réponse: $TEST_RESULT"
                fi
            fi
        else
            log "❌ Job Parser ne répond toujours pas"
        fi
    else
        log "❌ Aucun conteneur à redémarrer"
    fi
fi

echo ""
log "🎯 Diagnostic Job Parser V2 terminé"

# 6. Vérification finale de tous les services
echo ""
echo "📊 === ÉTAT FINAL DES SERVICES ==="

echo "CV Parser V2 (5051):"
curl -s http://localhost:5051/health > /dev/null && echo " ✅ Actif" || echo " ❌ Inactif"

echo "Job Parser V2 (5053):"
curl -s http://localhost:5053/health > /dev/null && echo " ✅ Actif" || echo " ❌ Inactif"

echo "Enhanced API V2.1 (5055):"
curl -s http://localhost:5055/health > /dev/null && echo " ✅ Actif" || echo " ❌ Inactif"

echo ""
echo "🏁 Si le Job Parser fonctionne maintenant, vous pouvez tester le système complet !"
