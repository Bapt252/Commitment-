#!/bin/bash

# 🎯 SuperSmartMatch V2.1 Enhanced - Résolution CV Parser & Tests Complets
# Script tout-en-un pour résoudre le port 5051 et valider le système

echo "🎯 === SUPERSMARTMATCH V2.1 ENHANCED - RÉSOLUTION COMPLÈTE ==="
echo "Résolution CV Parser V2 (port 5051) + Tests de validation"
echo ""

# Configuration
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="ssm_v21_fix_${TIMESTAMP}.log"

# Fonction de logging
log() {
    local message="[$(date '+%H:%M:%S')] $1"
    echo "$message"
    echo "$message" >> "$LOG_FILE"
}

log "🚀 Début de la résolution SuperSmartMatch V2.1 Enhanced"

# 1. PHASE 1: DIAGNOSTIC
echo ""
echo "🔍 === PHASE 1: DIAGNOSTIC INITIAL ==="
echo ""

log "Vérification de l'état des services..."

# Vérification Enhanced API V2.1 (critique)
if curl -s http://localhost:5055/health > /dev/null; then
    log "✅ Enhanced API V2.1 (5055): ACTIF"
    API_V21_OK=true
else
    log "❌ Enhanced API V2.1 (5055): INACTIF"
    API_V21_OK=false
fi

# Vérification Job Parser V2
if curl -s http://localhost:5053/health > /dev/null; then
    log "✅ Job Parser V2 (5053): ACTIF"
    JOB_PARSER_OK=true
else
    log "❌ Job Parser V2 (5053): INACTIF"
    JOB_PARSER_OK=false
fi

# Vérification CV Parser V2 (à réparer)
if curl -s http://localhost:5051/health > /dev/null; then
    log "✅ CV Parser V2 (5051): ACTIF - Pas de réparation nécessaire"
    CV_PARSER_OK=true
    NEED_FIX=false
else
    log "❌ CV Parser V2 (5051): INACTIF - Réparation nécessaire"
    CV_PARSER_OK=false
    NEED_FIX=true
fi

# 2. PHASE 2: RÉPARATION CV PARSER (si nécessaire)
if [ "$NEED_FIX" = true ]; then
    echo ""
    echo "🔧 === PHASE 2: RÉPARATION CV PARSER V2 ==="
    echo ""
    
    log "Début de la réparation du CV Parser V2..."
    
    # Arrêt des services existants
    log "🛑 Arrêt des conteneurs CV Parser existants..."
    docker kill $(docker ps -q --filter 'publish=5051') 2>/dev/null && log "✅ Conteneur arrêté" || log "ℹ️  Aucun conteneur sur 5051"
    docker rm $(docker ps -aq --filter 'publish=5051') 2>/dev/null && log "✅ Conteneur supprimé" || log "ℹ️  Aucun conteneur à supprimer"
    
    # Vérification des fichiers critiques
    log "📁 Vérification des fichiers critiques..."
    
    if [ ! -d "cv-parser-v2" ]; then
        log "❌ ERREUR CRITIQUE: Répertoire cv-parser-v2/ manquant"
        echo "Assurez-vous d'être dans le répertoire racine du projet"
        exit 1
    fi
    
    cd cv-parser-v2
    
    MISSING_FILES=false
    
    if [ ! -f "app.py" ]; then
        log "❌ ERREUR: app.py manquant"
        MISSING_FILES=true
    fi
    
    if [ ! -f "Dockerfile" ]; then
        log "❌ ERREUR: Dockerfile manquant"
        MISSING_FILES=true
    fi
    
    if [ ! -f "parsers/fix-pdf-extraction.js" ]; then
        log "❌ ERREUR: fix-pdf-extraction.js manquant"
        MISSING_FILES=true
    fi
    
    if [ ! -f "parsers/enhanced-mission-parser.js" ]; then
        log "❌ ERREUR: enhanced-mission-parser.js manquant"
        MISSING_FILES=true
    fi
    
    if [ "$MISSING_FILES" = true ]; then
        log "❌ ÉCHEC: Fichiers critiques manquants pour CV Parser V2"
        exit 1
    fi
    
    log "✅ Tous les fichiers critiques présents"
    
    # Reconstruction de l'image Docker
    log "🏗️  Reconstruction de l'image CV Parser V2..."
    docker build -t cv-parser-v2-fixed . --no-cache
    
    if [ $? -ne 0 ]; then
        log "❌ ÉCHEC: Construction Docker échouée"
        exit 1
    fi
    
    log "✅ Image Docker reconstruite avec succès"
    
    # Démarrage du nouveau conteneur
    log "🚀 Démarrage du nouveau conteneur..."
    docker run -d \
        -p 5051:5051 \
        --name cv-parser-v2-fixed-${TIMESTAMP} \
        --restart unless-stopped \
        cv-parser-v2-fixed
    
    if [ $? -ne 0 ]; then
        log "❌ ÉCHEC: Démarrage du conteneur échoué"
        exit 1
    fi
    
    log "✅ Conteneur démarré: cv-parser-v2-fixed-${TIMESTAMP}"
    
    # Attente du démarrage
    log "⏳ Attente du démarrage (20 secondes)..."
    sleep 20
    
    # Vérification de la réparation
    log "🔍 Vérification de la réparation..."
    for i in {1..6}; do
        if curl -s http://localhost:5051/health > /dev/null; then
            log "✅ CV Parser V2 réparé avec succès !"
            CV_PARSER_OK=true
            break
        else
            log "⏳ Tentative $i/6 - en attente..."
            sleep 5
        fi
    done
    
    if [ "$CV_PARSER_OK" = false ]; then
        log "❌ ÉCHEC: CV Parser V2 ne répond toujours pas"
        log "🚨 Logs du conteneur:"
        docker logs --tail 30 cv-parser-v2-fixed-${TIMESTAMP}
        exit 1
    fi
    
    cd ..
else
    log "ℹ️  CV Parser V2 déjà fonctionnel, passage aux tests"
fi

# 3. PHASE 3: VALIDATION SYSTÈME
echo ""
echo "✅ === PHASE 3: VALIDATION SYSTÈME V2.1 ==="
echo ""

log "Tests de validation du système complet..."

# Test Hugo Salvat (validation critique V2.1)
if [ "$API_V21_OK" = true ]; then
    log "👨‍💼 Test du cas Hugo Salvat (validation V2.1)..."
    
    HUGO_RESPONSE=$(curl -s http://localhost:5055/api/test/hugo-salvat)
    
    if [ $? -eq 0 ]; then
        SCORE=$(echo "$HUGO_RESPONSE" | grep -o '"total_score":[0-9]*' | grep -o '[0-9]*')
        
        if [ ! -z "$SCORE" ]; then
            log "📊 Score Hugo Salvat: ${SCORE}%"
            
            if [ "$SCORE" -lt 30 ]; then
                log "✅ SUCCÈS V2.1: Score faible détecté (${SCORE}% < 30%)"
                HUGO_TEST_OK=true
            else
                log "⚠️  ATTENTION: Score élevé (${SCORE}%) - vérifier logique V2.1"
                HUGO_TEST_OK=false
            fi
        else
            log "❌ Impossible d'extraire le score Hugo Salvat"
            HUGO_TEST_OK=false
        fi
        
        # Vérification alertes
        if echo "$HUGO_RESPONSE" | grep -q "domain_incompatibility"; then
            log "✅ Alerte d'incompatibilité métier détectée"
        else
            log "⚠️  Alerte d'incompatibilité manquante"
        fi
    else
        log "❌ Échec test Hugo Salvat"
        HUGO_TEST_OK=false
    fi
else
    log "❌ Impossible de tester Hugo Salvat - Enhanced API V2.1 inactif"
    HUGO_TEST_OK=false
fi

# 4. PHASE 4: TESTS AVEC FICHIERS RÉELS
echo ""
echo "📄 === PHASE 4: TESTS FICHIERS RÉELS ==="
echo ""

BATU_CV="$HOME/Desktop/BATU Sam.pdf"
IT_JOB="$HOME/Desktop/IT .pdf"

REAL_FILES_OK=false

if [ -f "$BATU_CV" ] && [ -f "$IT_JOB" ]; then
    log "✅ Fichiers de test trouvés:"
    log "   CV: $BATU_CV"
    log "   Job: $IT_JOB"
    
    if [ "$CV_PARSER_OK" = true ] && [ "$JOB_PARSER_OK" = true ] && [ "$API_V21_OK" = true ]; then
        log "🎯 Test de matching Enhanced V2.1 avec fichiers réels..."
        
        MATCHING_RESULT=$(curl -s -X POST \
            -F "cv_file=@$BATU_CV" \
            -F "job_file=@$IT_JOB" \
            http://localhost:5055/api/matching/files)
        
        if echo "$MATCHING_RESULT" | grep -q '"status":"success"'; then
            MATCH_SCORE=$(echo "$MATCHING_RESULT" | grep -o '"total_score":[0-9]*' | grep -o '[0-9]*')
            
            if [ ! -z "$MATCH_SCORE" ]; then
                log "📊 Score BATU vs IT: ${MATCH_SCORE}%"
                
                if [ "$MATCH_SCORE" -gt 70 ]; then
                    log "✅ EXCELLENT: Score > 70%"
                elif [ "$MATCH_SCORE" -gt 50 ]; then
                    log "✅ BON: Score > 50%"
                else
                    log "ℹ️  Score: ${MATCH_SCORE}%"
                fi
                
                REAL_FILES_OK=true
            else
                log "❌ Impossible d'extraire le score de matching"
            fi
        else
            log "❌ Échec du matching avec fichiers réels"
            log "Erreur: $(echo "$MATCHING_RESULT" | grep -o '"error":"[^"]*"')"
        fi
    else
        log "❌ Services manquants pour test fichiers réels"
    fi
else
    log "⚠️  Fichiers de test non trouvés:"
    log "   Attendu: $BATU_CV"
    log "   Attendu: $IT_JOB"
fi

# 5. PHASE 5: RAPPORT FINAL
echo ""
echo "📊 === RAPPORT FINAL ==="
echo ""

GLOBAL_SUCCESS=true

log "=== ÉTAT DES SERVICES ==="
if [ "$CV_PARSER_OK" = true ]; then
    log "✅ CV Parser V2 (5051): FONCTIONNEL"
else
    log "❌ CV Parser V2 (5051): NON FONCTIONNEL"
    GLOBAL_SUCCESS=false
fi

if [ "$JOB_PARSER_OK" = true ]; then
    log "✅ Job Parser V2 (5053): FONCTIONNEL"
else
    log "❌ Job Parser V2 (5053): NON FONCTIONNEL"
    GLOBAL_SUCCESS=false
fi

if [ "$API_V21_OK" = true ]; then
    log "✅ Enhanced API V2.1 (5055): FONCTIONNEL"
else
    log "❌ Enhanced API V2.1 (5055): NON FONCTIONNEL"
    GLOBAL_SUCCESS=false
fi

log "=== VALIDATION V2.1 ==="
if [ "$HUGO_TEST_OK" = true ]; then
    log "✅ Test Hugo Salvat: VALIDÉ (faux positif évité)"
else
    log "❌ Test Hugo Salvat: ÉCHEC"
    GLOBAL_SUCCESS=false
fi

if [ "$REAL_FILES_OK" = true ]; then
    log "✅ Test fichiers réels: SUCCÈS"
else
    log "⚠️  Test fichiers réels: NON EFFECTUÉ ou ÉCHEC"
fi

echo ""

if [ "$GLOBAL_SUCCESS" = true ]; then
    echo "🎉 === SUCCÈS COMPLET ==="
    log "✅ SuperSmartMatch V2.1 Enhanced entièrement fonctionnel"
    log "✅ CV Parser V2 résolu et opérationnel"
    log "✅ Système prêt pour les tests en production"
    
    echo ""
    echo "🚀 PROCHAINES ÉTAPES RECOMMANDÉES:"
    echo "1. Tests en lot:"
    echo "   python test_matching_system.py --cvs-folder ~/Desktop/CV\\ TEST/ --jobs-folder ~/Desktop/FDP\\ TEST/"
    echo ""
    echo "2. Tests comparatifs V2 vs V2.1:"
    echo "   python test_matching_system.py --predefined-tests --output results_v21_${TIMESTAMP}.json"
    echo ""
    echo "3. Documentation des résultats:"
    echo "   Comparaison des scores avant/après V2.1"
    echo "   Validation des alertes d'incompatibilité"
    
else
    echo "⚠️  === PROBLÈMES DÉTECTÉS ==="
    log "❌ Certains composants ne fonctionnent pas correctement"
    log "❌ Intervention manuelle requise"
    
    echo ""
    echo "🔧 ACTIONS REQUISES:"
    
    if [ "$CV_PARSER_OK" = false ]; then
        echo "- Vérifier les logs CV Parser: docker logs cv-parser-v2-fixed-${TIMESTAMP}"
    fi
    
    if [ "$JOB_PARSER_OK" = false ]; then
        echo "- Redémarrer Job Parser V2"
    fi
    
    if [ "$API_V21_OK" = false ]; then
        echo "- Redémarrer Enhanced API V2.1: python api-matching-enhanced-v2.py"
    fi
fi

echo ""
log "📁 Log complet sauvegardé: $LOG_FILE"
log "🏁 Fin de l'exécution SuperSmartMatch V2.1 Enhanced"

# Affichage final des services
echo ""
echo "📋 État final des services:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(5051|5053|5055|cv-parser|job-parser)" || echo "Aucun conteneur Docker détecté"
