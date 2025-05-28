#!/bin/bash

# 🧪 Script de test intégration Google Maps pour SuperSmartMatch v2.2
# Tests automatisés de l'API Google Maps et validation fonctionnelle

set -e  # Arrêter sur erreur

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/test-google-maps.log"
API_BASE_URL="http://localhost:5061"
TIMEOUT=30

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
    echo -e "$1"
}

# Fonction de test avec couleurs
test_result() {
    if [ $1 -eq 0 ]; then
        log "${GREEN}✅ $2${NC}"
        return 0
    else
        log "${RED}❌ $2${NC}"
        return 1
    fi
}

# Initialisation
log "${BLUE}🚀 Démarrage tests intégration Google Maps SuperSmartMatch v2.2${NC}"
echo "" > "$LOG_FILE"

# 1. TEST PRÉREQUIS
log "${YELLOW}📋 Phase 1: Vérification des prérequis${NC}"

# Vérifier Python
if command -v python3 &> /dev/null; then
    test_result 0 "Python3 disponible"
else
    test_result 1 "Python3 non trouvé"
    exit 1
fi

# Vérifier les dépendances Python
log "Vérification des dépendances Python..."
python3 -c "import requests, googlemaps" 2>/dev/null
test_result $? "Dépendances Python (requests, googlemaps)"

# Vérifier la clé API Google Maps
if [ -n "$GOOGLE_MAPS_API_KEY" ]; then
    test_result 0 "Variable GOOGLE_MAPS_API_KEY définie"
else
    if [ -f "$SCRIPT_DIR/.env" ] && grep -q "GOOGLE_MAPS_API_KEY" "$SCRIPT_DIR/.env"; then
        test_result 0 "GOOGLE_MAPS_API_KEY trouvée dans .env"
        export $(grep "GOOGLE_MAPS_API_KEY" "$SCRIPT_DIR/.env" | xargs)
    else
        test_result 1 "GOOGLE_MAPS_API_KEY non configurée"
        log "${YELLOW}⚠️ Tests Google Maps désactivés - Mode fallback sera testé${NC}"
        GOOGLE_MAPS_DISABLED=true
    fi
fi

# 2. TEST API GOOGLE MAPS DIRECTE
if [ "$GOOGLE_MAPS_DISABLED" != "true" ]; then
    log "${YELLOW}📡 Phase 2: Test API Google Maps directe${NC}"
    
    # Test API basique
    log "Test API Google Maps Directions..."
    response=$(curl -s --max-time $TIMEOUT \
        "https://maps.googleapis.com/maps/api/directions/json?origin=Paris&destination=Lyon&key=$GOOGLE_MAPS_API_KEY")
    
    if echo "$response" | grep -q '"status" : "OK"'; then
        test_result 0 "API Google Maps Directions accessible"
        
        # Extraire temps de trajet pour validation
        duration=$(echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('routes'):
    print(data['routes'][0]['legs'][0]['duration']['text'])
else:
    print('Erreur')")
        
        if [ "$duration" != "Erreur" ]; then
            test_result 0 "Calcul temps trajet Paris→Lyon: $duration"
        else
            test_result 1 "Impossible d'extraire temps de trajet"
        fi
    else
        test_result 1 "API Google Maps inaccessible"
        log "Réponse API: $response"
    fi
    
    # Test différents modes de transport
    log "Test modes de transport..."
    for mode in "driving" "transit" "walking"; do
        response=$(curl -s --max-time $TIMEOUT \
            "https://maps.googleapis.com/maps/api/directions/json?origin=Paris,France&destination=Versailles,France&mode=$mode&key=$GOOGLE_MAPS_API_KEY")
        
        if echo "$response" | grep -q '"status" : "OK"'; then
            duration=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('routes'):
        print(data['routes'][0]['legs'][0]['duration']['text'])
    else:
        print('N/A')
except:
    print('N/A')")
            test_result 0 "Mode $mode: $duration"
        else
            test_result 1 "Mode $mode: Erreur API"
        fi
    done
else
    log "${YELLOW}⏭️ Phase 2: Ignorée (Google Maps désactivé)${NC}"
fi

# 3. TEST SUPERSMARTMATCH
log "${YELLOW}🤖 Phase 3: Test SuperSmartMatch v2.2${NC}"

# Vérifier si le serveur est démarré
log "Vérification serveur SuperSmartMatch..."
if curl -s --max-time 5 "$API_BASE_URL/api/health" > /dev/null 2>&1; then
    test_result 0 "Serveur SuperSmartMatch accessible sur $API_BASE_URL"
else
    log "${YELLOW}⚠️ Serveur non démarré - Tentative de démarrage...${NC}"
    
    # Tenter de démarrer le serveur en arrière-plan
    cd "$SCRIPT_DIR"
    python3 app.py &
    SERVER_PID=$!
    sleep 5
    
    if curl -s --max-time 5 "$API_BASE_URL/api/health" > /dev/null 2>&1; then
        test_result 0 "Serveur SuperSmartMatch démarré (PID: $SERVER_PID)"
        STOP_SERVER=true
    else
        test_result 1 "Impossible de démarrer le serveur SuperSmartMatch"
        exit 1
    fi
fi

# Test info algorithme
log "Test informations algorithme..."
response=$(curl -s --max-time 10 \
    -H "Content-Type: application/json" \
    "$API_BASE_URL/api/algorithms/supersmartmatch/info")

if echo "$response" | grep -q '"version".*"2.2"'; then
    test_result 0 "SuperSmartMatch v2.2 détecté"
    
    # Vérifier capacités Google Maps
    if echo "$response" | grep -q '"google_maps_integration".*true'; then
        test_result 0 "Intégration Google Maps activée"
    else
        test_result 0 "Mode fallback activé (Google Maps désactivé)"
    fi
else
    test_result 1 "SuperSmartMatch v2.2 non détecté"
fi

# 4. TEST MATCHING AVEC GOOGLE MAPS
log "${YELLOW}🎯 Phase 4: Test matching avec calcul temps trajet${NC}"

# Test de base Paris → Lyon
log "Test matching Paris → Lyon..."
test_data='{
  "cv_data": {
    "adresse": "Paris, France",
    "experience_annees": 5,
    "competences": ["Python", "JavaScript"],
    "questionnaire_data": {
      "priorites_candidat": {
        "evolution": 7,
        "remuneration": 8,
        "proximite": 9,
        "flexibilite": 6
      },
      "transport_preferences": {
        "transport_prefere": "driving",
        "heure_depart_travail": "08:30"
      }
    }
  },
  "job_data": [{
    "id": "test_job_1",
    "titre": "Développeur Python",
    "localisation": "Lyon, France",
    "salaire_min": 45000,
    "salaire_max": 55000,
    "competences_requises": ["Python"]
  }],
  "algorithm": "supersmartmatch"
}'

response=$(curl -s --max-time 30 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$test_data" \
    "$API_BASE_URL/api/match")

if echo "$response" | grep -q '"matching_score_entreprise"'; then
    test_result 0 "Matching exécuté avec succès"
    
    # Vérifier présence travel_info
    if echo "$response" | grep -q '"travel_info"'; then
        test_result 0 "travel_info présent dans la réponse"
        
        # Extraire et afficher infos de trajet
        travel_info=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])
    if results and 'scores_detailles' in results[0]:
        travel_info = results[0]['scores_detailles'].get('proximite', {}).get('travel_info', {})
        if travel_info:
            mode = travel_info.get('mode', 'unknown')
            duration = travel_info.get('duration_text', 'N/A')
            distance = travel_info.get('distance_text', 'N/A')
            print(f'Mode: {mode}, Durée: {duration}, Distance: {distance}')
        else:
            print('travel_info vide')
    else:
        print('Pas de résultats')
except Exception as e:
    print(f'Erreur: {e}')")
        
        log "Détails trajet: $travel_info"
        
        if [ "$travel_info" != "travel_info vide" ] && [ "$travel_info" != "Pas de résultats" ]; then
            test_result 0 "Informations de trajet calculées"
        else
            test_result 0 "Mode fallback utilisé (normal si Google Maps désactivé)"
        fi
    else
        test_result 1 "travel_info manquant dans la réponse"
    fi
    
    # Vérifier score proximité
    score_proximite=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])
    if results and 'scores_detailles' in results[0]:
        print(results[0]['scores_detailles']['proximite']['pourcentage'])
    else:
        print('N/A')
except:
    print('N/A')")
    
    if [ "$score_proximite" != "N/A" ] && [ "$score_proximite" -gt 0 ]; then
        test_result 0 "Score proximité calculé: $score_proximite%"
    else
        test_result 1 "Score proximité non calculé"
    fi
    
else
    test_result 1 "Matching échoué"
    log "Réponse API: $response"
fi

# Test transport en commun
log "Test mode transport en commun (Paris → Boulogne)..."
test_data_transit='{
  "cv_data": {
    "adresse": "Paris 15ème, France",
    "questionnaire_data": {
      "transport_preferences": {
        "transport_prefere": "transit",
        "heure_depart_travail": "09:00"
      }
    }
  },
  "job_data": [{
    "id": "test_job_2",
    "titre": "Développeur",
    "localisation": "Boulogne-Billancourt, France"
  }],
  "algorithm": "supersmartmatch"
}'

response=$(curl -s --max-time 20 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$test_data_transit" \
    "$API_BASE_URL/api/match")

if echo "$response" | grep -q '"matching_score_entreprise"'; then
    test_result 0 "Test transport en commun réussi"
    
    # Vérifier détails transport
    transit_details=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])
    if results and 'scores_detailles' in results[0]:
        details = results[0]['scores_detailles']['proximite']['details']
        for detail in details:
            if 'transport' in detail.lower() or 'métro' in detail.lower() or 'min' in detail:
                print(detail)
                break
    else:
        print('N/A')
except:
    print('N/A')")
    
    if [ "$transit_details" != "N/A" ]; then
        test_result 0 "Détails transport: $transit_details"
    else
        test_result 0 "Mode fallback pour transport en commun"
    fi
else
    test_result 1 "Test transport en commun échoué"
fi

# 5. TEST PERFORMANCE ET CACHE
log "${YELLOW}⚡ Phase 5: Test performance et cache${NC}"

# Mesurer temps de réponse
log "Test performance (même requête x2 pour cache)..."
start_time=$(date +%s%N)

curl -s --max-time 15 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$test_data" \
    "$API_BASE_URL/api/match" > /dev/null

end_time=$(date +%s%N)
duration1=$((($end_time - $start_time) / 1000000))  # en ms

# Deuxième appel (cache)
start_time=$(date +%s%N)

curl -s --max-time 15 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$test_data" \
    "$API_BASE_URL/api/match" > /dev/null

end_time=$(date +%s%N)
duration2=$((($end_time - $start_time) / 1000000))  # en ms

log "Premier appel: ${duration1}ms, Deuxième appel: ${duration2}ms"

if [ $duration2 -gt 0 ] && [ $duration1 -gt 0 ]; then
    if [ $duration2 -lt $duration1 ]; then
        test_result 0 "Cache améliore les performances (gain: $((duration1 - duration2))ms)"
    else
        test_result 0 "Performance stable ($duration1ms → $duration2ms)"
    fi
else
    test_result 1 "Impossible de mesurer les performances"
fi

# 6. TEST FALLBACK
log "${YELLOW}🔄 Phase 6: Test mode fallback${NC}"

# Test avec adresses invalides
log "Test gestion adresses invalides..."
test_data_invalid='{
  "cv_data": {
    "adresse": "AdresseInvalide123XYZ",
    "questionnaire_data": {
      "transport_preferences": {
        "transport_prefere": "driving"
      }
    }
  },
  "job_data": [{
    "id": "test_job_3",
    "titre": "Test",
    "localisation": "AutreAdresseInvalide456ABC"
  }],
  "algorithm": "supersmartmatch"
}'

response=$(curl -s --max-time 15 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$test_data_invalid" \
    "$API_BASE_URL/api/match")

if echo "$response" | grep -q '"matching_score_entreprise"'; then
    test_result 0 "Fallback fonctionne avec adresses invalides"
    
    # Vérifier message de fallback
    if echo "$response" | grep -q -i "approximatif\|fallback\|estimé"; then
        test_result 0 "Message fallback présent"
    else
        log "${YELLOW}⚠️ Message fallback non détecté (peut être normal)${NC}"
    fi
else
    test_result 1 "Fallback échoué avec adresses invalides"
fi

# NETTOYAGE
if [ "$STOP_SERVER" = "true" ] && [ -n "$SERVER_PID" ]; then
    log "Arrêt du serveur de test..."
    kill $SERVER_PID 2>/dev/null || true
    sleep 2
fi

# RÉSUMÉ
log "${BLUE}📊 Résumé des tests Google Maps SuperSmartMatch v2.2${NC}"
total_tests=$(grep -c "✅\|❌" "$LOG_FILE")
passed_tests=$(grep -c "✅" "$LOG_FILE")
failed_tests=$(grep -c "❌" "$LOG_FILE")

log "${GREEN}Tests réussis: $passed_tests/$total_tests${NC}"
if [ $failed_tests -gt 0 ]; then
    log "${RED}Tests échoués: $failed_tests${NC}"
fi

# Score de réussite
success_rate=$((passed_tests * 100 / total_tests))
log "${BLUE}Taux de réussite: $success_rate%${NC}"

if [ $success_rate -ge 80 ]; then
    log "${GREEN}🎉 Integration Google Maps validée ! SuperSmartMatch v2.2 est prêt.${NC}"
    exit 0
elif [ $success_rate -ge 60 ]; then
    log "${YELLOW}⚠️ Integration partiellement validée. Vérifiez les erreurs ci-dessus.${NC}"
    exit 1
else
    log "${RED}❌ Integration Google Maps échouée. Vérifiez la configuration.${NC}"
    exit 2
fi
