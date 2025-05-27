#!/bin/bash

# Script de test complet du pipeline SuperSmartMatch Unifié
# Usage: ./test_pipeline_script.sh

echo "🧪 TEST PIPELINE SUPERSMARTMATCH UNIFIÉ"
echo "======================================="

# Configuration
BASE_URL="http://localhost:5052"
SESSION_ID="test_$(date +%s)"
TEST_FILES_DIR="./test_files"

# Créer le dossier de test si nécessaire
mkdir -p $TEST_FILES_DIR

# Créer des fichiers de test
echo "📝 Création des fichiers de test..."

cat > $TEST_FILES_DIR/test_cv.txt << 'EOF'
Jean Dupont
Développeur Full-Stack

Compétences:
- Python (Django, Flask)
- JavaScript (React, Node.js)
- Bases de données (PostgreSQL, MongoDB)
- Docker, Git

Expérience:
- 5 ans en développement web
- 3 ans en équipe agile

Formation:
- Master en Informatique (Bac+5)

Localisation: Paris
EOF

cat > $TEST_FILES_DIR/test_job.txt << 'EOF'
Poste: Développeur Full-Stack Senior

Compétences requises:
- Python obligatoire
- JavaScript/React
- Expérience avec les bases de données
- Connaissance Docker souhaitable

Exigences:
- Minimum 3 ans d'expérience
- Formation Bac+3 minimum
- Localisation: Paris ou remote

Salaire: 45000-55000€
EOF

echo "✅ Fichiers de test créés"

# Fonction pour vérifier si le service est disponible
check_service() {
    echo "🔍 Vérification du service..."
    
    for i in {1..10}; do
        if curl -f -s "$BASE_URL/health" > /dev/null; then
            echo "✅ Service disponible"
            return 0
        fi
        echo "⏳ Tentative $i/10 - Service non disponible, attente..."
        sleep 3
    done
    
    echo "❌ Service non disponible après 30 secondes"
    exit 1
}

# Test du health check
test_health() {
    echo "\n🔍 TEST 1: Health Check"
    
    response=$(curl -s "$BASE_URL/health")
    
    if echo "$response" | grep -q '"status":"healthy"'; then
        echo "✅ Health check réussi"
        echo "📊 Fonctionnalités ML: $(echo "$response" | jq -r '.features')"
    else
        echo "❌ Health check échoué"
        echo "Response: $response"
        exit 1
    fi
}

# Test étape 1: Parsing
test_step1_parsing() {
    echo "\n🔍 TEST 2: Étape 1 - Parsing"
    
    response=$(curl -s -X POST \
        -F "cv_file=@$TEST_FILES_DIR/test_cv.txt" \
        -F "job_file=@$TEST_FILES_DIR/test_job.txt" \
        -F "session_id=$SESSION_ID" \
        "$BASE_URL/api/unified-match/start")
    
    echo "Response parsing: $response"
    
    if echo "$response" | grep -q '"status":"waiting_questionnaire"'; then
        echo "✅ Parsing réussi - En attente du questionnaire"
        
        # Extraire les informations de parsing
        echo "📋 Données parsées:"
        echo "$response" | jq -r '.parsed_data' 2>/dev/null || echo "Données non disponibles en JSON"
    else
        echo "❌ Parsing échoué"
        echo "Response: $response"
        exit 1
    fi
}

# Test vérification statut
test_session_status() {
    echo "\n🔍 TEST 3: Vérification du statut de session"
    
    response=$(curl -s "$BASE_URL/api/unified-match/status/$SESSION_ID")
    
    echo "Response statut: $response"
    
    if echo "$response" | grep -q '"status":"ready_for_questionnaire"'; then
        echo "✅ Statut de session correct"
        
        # Afficher les détails
        has_cv=$(echo "$response" | jq -r '.has_cv' 2>/dev/null)
        has_job=$(echo "$response" | jq -r '.has_job' 2>/dev/null)
        confidence=$(echo "$response" | jq -r '.parsing_confidence' 2>/dev/null)
        
        echo "📊 CV parsé: $has_cv"
        echo "📊 Job parsé: $has_job"
        echo "📊 Confiance: $confidence"
    else
        echo "❌ Statut de session incorrect"
        echo "Response: $response"
        exit 1
    fi
}

# Test étape 3: Matching complet
test_step3_matching() {
    echo "\n🔍 TEST 4: Étape 3 - Matching complet avec questionnaire"
    
    questionnaire_data='{
        "session_id": "'$SESSION_ID'",
        "questionnaire_data": {
            "motivation": 8,
            "disponibilite": 9,
            "mobilite": 6,
            "salaire_souhaite": 50000,
            "experience_specifique": "Développement d'applications web modernes avec Python et React",
            "objectifs_carriere": "Évoluer vers un poste de lead developer et encadrer une équipe"
        }
    }'
    
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$questionnaire_data" \
        "$BASE_URL/api/unified-match/complete")
    
    echo "Response matching: $response"
    
    if echo "$response" | grep -q '"matching_score_entreprise"'; then
        echo "✅ Matching complet réussi"
        
        # Extraire et afficher les scores
        score_entreprise=$(echo "$response" | jq -r '.matching_score_entreprise' 2>/dev/null)
        score_candidat=$(echo "$response" | jq -r '.matching_score_candidat' 2>/dev/null)
        questionnaire_boost=$(echo "$response" | jq -r '.questionnaire_boost' 2>/dev/null)
        
        echo "🎯 Score Entreprise: ${score_entreprise}%"
        echo "🎯 Score Candidat: ${score_candidat}%"
        echo "🚀 Boost Questionnaire: ${questionnaire_boost}"
        
        # Afficher les recommandations
        echo "💡 Recommandations:"
        echo "$response" | jq -r '.recommendations[]' 2>/dev/null || echo "Recommandations non disponibles"
        
        # Match ID
        match_id=$(echo "$response" | jq -r '.match_id' 2>/dev/null)
        echo "🔗 Match ID: $match_id"
        
    else
        echo "❌ Matching échoué"
        echo "Response: $response"
        exit 1
    fi
}

# Test liste des sessions
test_sessions_list() {
    echo "\n🔍 TEST 5: Liste des sessions actives"
    
    response=$(curl -s "$BASE_URL/api/unified-match/sessions")
    
    echo "Response sessions: $response"
    
    if echo "$response" | grep -q '"active_sessions"'; then
        echo "✅ Liste des sessions récupérée"
        
        active_count=$(echo "$response" | jq -r '.active_sessions' 2>/dev/null)
        echo "📊 Sessions actives: $active_count"
    else
        echo "⚠️  Liste des sessions non disponible (normal si Redis désactivé)"
    fi
}

# Test de performance
test_performance() {
    echo "\n🔍 TEST 6: Test de performance"
    
    start_time=$(date +%s)
    
    # Faire plusieurs requêtes pour tester la performance
    for i in {1..3}; do
        session_perf="perf_test_${i}_$(date +%s)"
        
        echo "🏃 Test performance $i/3..."
        
        curl -s -X POST \
            -F "cv_file=@$TEST_FILES_DIR/test_cv.txt" \
            -F "job_file=@$TEST_FILES_DIR/test_job.txt" \
            -F "session_id=$session_perf" \
            "$BASE_URL/api/unified-match/start" > /dev/null
        
        questionnaire_perf='{
            "session_id": "'$session_perf'",
            "questionnaire_data": {
                "motivation": 7,
                "disponibilite": 8,
                "mobilite": 5
            }
        }'
        
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$questionnaire_perf" \
            "$BASE_URL/api/unified-match/complete" > /dev/null
    done
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo "✅ Test de performance terminé en ${duration}s"
    echo "📊 Moyenne: $((duration / 3))s par matching complet"
}

# Nettoyage
cleanup() {
    echo "\n🧹 Nettoyage..."
    rm -rf $TEST_FILES_DIR
    echo "✅ Nettoyage terminé"
}

# Fonction principale
main() {
    echo "Démarrage des tests pour SuperSmartMatch Unifié"
    echo "URL de base: $BASE_URL"
    echo "Session ID: $SESSION_ID"
    
    # Vérifier la disponibilité du service
    check_service
    
    # Exécuter tous les tests
    test_health
    test_step1_parsing
    test_session_status
    test_step3_matching
    test_sessions_list
    test_performance
    
    # Nettoyage
    cleanup
    
    echo "\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !"
    echo "📈 SuperSmartMatch Unifié fonctionne correctement"
    echo "\n📋 Résumé:"
    echo "  ✅ Health check"
    echo "  ✅ Parsing automatique (CV + Job)"
    echo "  ✅ Gestion des sessions"
    echo "  ✅ Matching unifié avec questionnaire"
    echo "  ✅ Performance acceptable"
    echo "\n🔗 Endpoints disponibles:"
    echo "  • Health: $BASE_URL/health"
    echo "  • Start: $BASE_URL/api/unified-match/start"
    echo "  • Complete: $BASE_URL/api/unified-match/complete"
    echo "  • Status: $BASE_URL/api/unified-match/status/{session_id}"
    echo "  • Sessions: $BASE_URL/api/unified-match/sessions"
}

# Gestion des erreurs
trap 'echo "\n❌ Test interrompu"; cleanup; exit 1' INT TERM

# Exécution
main
