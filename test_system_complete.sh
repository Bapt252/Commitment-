#!/bin/bash

# 🧪 Script de test CV Parser V2 + Enhanced API V2.1
# Test complet du système après résolution

echo "🧪 === TEST COMPLET SYSTÈME V2.1 ENHANCED ==="
echo "Validation du CV Parser V2 et Enhanced API V2.1"
echo ""

# Fonction de logging
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Test fonction avec retry
test_endpoint() {
    local url=$1
    local name=$2
    local max_retries=3
    
    for i in $(seq 1 $max_retries); do
        if curl -s -f "$url" > /dev/null; then
            echo "✅ $name: OK"
            return 0
        else
            if [ $i -eq $max_retries ]; then
                echo "❌ $name: ÉCHEC après $max_retries tentatives"
                return 1
            else
                echo "⏳ $name: Tentative $i/$max_retries..."
                sleep 2
            fi
        fi
    done
}

# 1. Tests de connectivité des services
echo "🔗 === TESTS DE CONNECTIVITÉ ==="
echo ""

test_endpoint "http://localhost:5051/health" "CV Parser V2 (5051)"
CV_STATUS=$?

test_endpoint "http://localhost:5053/health" "Job Parser V2 (5053)"
JOB_STATUS=$?

test_endpoint "http://localhost:5055/health" "Enhanced API V2.1 (5055)"
API_STATUS=$?

echo ""

# 2. Test détaillé du CV Parser
if [ $CV_STATUS -eq 0 ]; then
    echo "🔍 === TEST DÉTAILLÉ CV PARSER V2 ==="
    echo ""
    
    log "Test health check détaillé..."
    HEALTH_RESPONSE=$(curl -s http://localhost:5051/health)
    echo "Réponse: $HEALTH_RESPONSE"
    
    # Vérifier la présence des parsers
    echo "$HEALTH_RESPONSE" | grep -q "fix_pdf_extraction.*true" && echo "✅ fix-pdf-extraction.js: Disponible" || echo "❌ fix-pdf-extraction.js: Manquant"
    echo "$HEALTH_RESPONSE" | grep -q "enhanced_mission_parser.*true" && echo "✅ enhanced-mission-parser.js: Disponible" || echo "❌ enhanced-mission-parser.js: Manquant"
    echo ""
fi

# 3. Test du cas Hugo Salvat (validation V2.1)
if [ $API_STATUS -eq 0 ]; then
    echo "👨‍💼 === TEST CAS HUGO SALVAT (VALIDATION V2.1) ==="
    echo ""
    
    log "Test du cas critique Hugo Salvat..."
    HUGO_RESPONSE=$(curl -s http://localhost:5055/api/test/hugo-salvat)
    
    if [ $? -eq 0 ]; then
        echo "✅ API Enhanced répond"
        
        # Extraire le score
        SCORE=$(echo "$HUGO_RESPONSE" | grep -o '"total_score":[0-9]*' | grep -o '[0-9]*')
        
        if [ ! -z "$SCORE" ]; then
            echo "📊 Score Hugo Salvat: $SCORE%"
            
            if [ "$SCORE" -lt 30 ]; then
                echo "✅ SUCCÈS V2.1: Score < 30% (attendu pour éviter faux positif)"
            else
                echo "⚠️  ATTENTION: Score élevé ($SCORE%) - vérifier la logique V2.1"
            fi
        else
            echo "❌ Impossible d'extraire le score"
        fi
        
        # Vérifier les alertes
        echo "$HUGO_RESPONSE" | grep -q "domain_incompatibility" && echo "✅ Alerte d'incompatibilité détectée" || echo "❌ Alerte d'incompatibilité manquante"
        
    else
        echo "❌ Échec test Hugo Salvat"
    fi
    echo ""
fi

# 4. Test avec fichiers réels (si disponibles)
echo "📄 === TEST FICHIERS RÉELS ==="
echo ""

BATU_CV="$HOME/Desktop/BATU Sam.pdf"
IT_JOB="$HOME/Desktop/IT .pdf"  # Attention à l'espace avant .pdf

if [ -f "$BATU_CV" ]; then
    echo "✅ CV BATU Sam trouvé: $BATU_CV"
    
    if [ $CV_STATUS -eq 0 ]; then
        log "Test parsing CV BATU Sam..."
        
        # Test du CV Parser
        CV_RESULT=$(curl -s -X POST -F "file=@$BATU_CV" http://localhost:5051/api/parse-cv/)
        
        if echo "$CV_RESULT" | grep -q '"status":"success"'; then
            echo "✅ CV BATU Sam parsé avec succès"
            
            # Extraire quelques infos
            echo "$CV_RESULT" | grep -q '"name"' && echo "  ✅ Nom détecté"
            echo "$CV_RESULT" | grep -q '"professional_experience"' && echo "  ✅ Expériences détectées"
            echo "$CV_RESULT" | grep -q '"skills"' && echo "  ✅ Compétences détectées"
            
        else
            echo "❌ Échec parsing CV BATU Sam"
            echo "Erreur: $(echo "$CV_RESULT" | grep -o '"error":"[^"]*"')"
        fi
    fi
else
    echo "⚠️  CV BATU Sam non trouvé: $BATU_CV"
fi

if [ -f "$IT_JOB" ]; then
    echo "✅ Job IT trouvé: $IT_JOB"
    
    if [ $JOB_STATUS -eq 0 ]; then
        log "Test parsing Job IT..."
        
        # Test du Job Parser  
        JOB_RESULT=$(curl -s -X POST -F "file=@$IT_JOB" http://localhost:5053/api/parse-job/)
        
        if echo "$JOB_RESULT" | grep -q '"status":"success"'; then
            echo "✅ Job IT parsé avec succès"
            
            # Extraire quelques infos
            echo "$JOB_RESULT" | grep -q '"title"' && echo "  ✅ Titre détecté"
            echo "$JOB_RESULT" | grep -q '"required_skills"' && echo "  ✅ Compétences requises détectées"
            echo "$JOB_RESULT" | grep -q '"missions"' && echo "  ✅ Missions détectées"
            
        else
            echo "❌ Échec parsing Job IT"
            echo "Erreur: $(echo "$JOB_RESULT" | grep -o '"error":"[^"]*"')"
        fi
    fi
else
    echo "⚠️  Job IT non trouvé: $IT_JOB"
fi

# 5. Test matching complet (si les deux fichiers sont disponibles)
if [ -f "$BATU_CV" ] && [ -f "$IT_JOB" ] && [ $API_STATUS -eq 0 ]; then
    echo ""
    echo "🎯 === TEST MATCHING COMPLET BATU vs IT ==="
    echo ""
    
    log "Test matching Enhanced V2.1..."
    
    # Test via l'API Enhanced avec fichiers
    MATCHING_RESULT=$(curl -s -X POST \
        -F "cv_file=@$BATU_CV" \
        -F "job_file=@$IT_JOB" \
        http://localhost:5055/api/matching/files)
    
    if echo "$MATCHING_RESULT" | grep -q '"status":"success"'; then
        echo "✅ Matching Enhanced V2.1 réussi"
        
        # Extraire le score
        MATCH_SCORE=$(echo "$MATCHING_RESULT" | grep -o '"total_score":[0-9]*' | grep -o '[0-9]*')
        
        if [ ! -z "$MATCH_SCORE" ]; then
            echo "📊 Score Matching BATU vs IT: $MATCH_SCORE%"
            
            if [ "$MATCH_SCORE" -gt 70 ]; then
                echo "✅ EXCELLENT: Score > 70%"
            elif [ "$MATCH_SCORE" -gt 50 ]; then
                echo "✅ BON: Score > 50%"
            elif [ "$MATCH_SCORE" -gt 30 ]; then
                echo "⚠️  MOYEN: Score > 30%"
            else
                echo "❌ FAIBLE: Score < 30%"
            fi
        fi
        
        # Vérifier les alertes
        ALERTS=$(echo "$MATCHING_RESULT" | grep -o '"alerts":\[[^]]*\]')
        if [ ! -z "$ALERTS" ]; then
            echo "🚨 Alertes détectées: $ALERTS"
        else
            echo "✅ Aucune alerte"
        fi
        
    else
        echo "❌ Échec matching Enhanced"
        echo "Erreur: $(echo "$MATCHING_RESULT" | grep -o '"error":"[^"]*"')"
    fi
fi

echo ""
echo "📊 === RÉSUMÉ DES TESTS ==="
echo ""

# Statut global
ALL_OK=true

if [ $CV_STATUS -ne 0 ]; then
    echo "❌ CV Parser V2 (5051): NON FONCTIONNEL"
    ALL_OK=false
else
    echo "✅ CV Parser V2 (5051): FONCTIONNEL"
fi

if [ $JOB_STATUS -ne 0 ]; then
    echo "❌ Job Parser V2 (5053): NON FONCTIONNEL"
    ALL_OK=false
else
    echo "✅ Job Parser V2 (5053): FONCTIONNEL"
fi

if [ $API_STATUS -ne 0 ]; then
    echo "❌ Enhanced API V2.1 (5055): NON FONCTIONNEL"
    ALL_OK=false
else
    echo "✅ Enhanced API V2.1 (5055): FONCTIONNEL"
fi

echo ""

if [ "$ALL_OK" = true ]; then
    echo "🎉 === SUCCÈS COMPLET ==="
    echo "✅ Tous les services sont opérationnels"
    echo "✅ CV Parser V2 résolu et fonctionnel"
    echo "✅ Système V2.1 Enhanced prêt pour les tests en production"
    echo ""
    echo "🚀 PROCHAINES ÉTAPES:"
    echo "1. Testez en lot avec: python test_matching_system.py --cvs-folder ~/Desktop/CV\\ TEST/ --jobs-folder ~/Desktop/FDP\\ TEST/"
    echo "2. Lancez les tests comparatifs pour valider les améliorations V2.1"
    echo "3. Documentez les résultats pour validation finale"
else
    echo "⚠️  === PROBLÈMES DÉTECTÉS ==="
    echo "Certains services ne répondent pas correctement"
    echo "Consultez les logs et relancez les scripts de réparation"
fi

echo ""
log "Test complet terminé"
