#!/bin/bash

# 🚀 SuperSmartMatch V2 - Script de Test Amélioré et Moderne
# Version: 2.0 - Tests complets avec validation avancée et métriques

set -e

# Configuration des couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration des services
SSM_V2_URL="http://localhost:5070"
NEXTEN_URL="http://localhost:5052"
SSM_V1_URL="http://localhost:5062"

# Statistiques de tests
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
START_TIME=$(date +%s)

# Fonction d'affichage avec timestamp
log() {
    echo -e "[$(date '+%H:%M:%S')] $1"
}

success() {
    log "${GREEN}✅ $1${NC}"
    ((PASSED_TESTS++))
}

error() {
    log "${RED}❌ $1${NC}"
    ((FAILED_TESTS++))
}

warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

info() {
    log "${BLUE}🔵 $1${NC}"
}

# Fonction de test avec validation JSON
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_status="${5:-200}"
    
    ((TOTAL_TESTS++))
    info "Test: $name"
    
    if [[ "$method" == "GET" ]]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "$expected_status" ]]; then
        success "$name - Status: $http_code"
        
        # Validation JSON si réponse non vide
        if [[ -n "$body" && "$body" != "null" ]]; then
            if echo "$body" | jq . >/dev/null 2>&1; then
                success "$name - JSON valide"
                return 0
            else
                error "$name - JSON invalide: $body"
                return 1
            fi
        fi
        return 0
    else
        error "$name - Status attendu: $expected_status, reçu: $http_code"
        warning "Réponse: $body"
        return 1
    fi
}

# Fonction de test de performance
test_performance() {
    local name="$1"
    local url="$2"
    local data="$3"
    local max_time_ms="${4:-1000}"
    
    ((TOTAL_TESTS++))
    info "Test Performance: $name (max: ${max_time_ms}ms)"
    
    start_time=$(date +%s%3N)
    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data" \
        -w "%{http_code}")
    end_time=$(date +%s%3N)
    
    duration=$((end_time - start_time))
    http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]] && [[ $duration -le $max_time_ms ]]; then
        success "$name - Durée: ${duration}ms (✓ < ${max_time_ms}ms)"
        return 0
    elif [[ "$http_code" != "200" ]]; then
        error "$name - Erreur HTTP: $http_code"
        return 1
    else
        warning "$name - Lent: ${duration}ms (> ${max_time_ms}ms acceptable)"
        return 0
    fi
}

# Banner de démarrage
echo
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              🚀 SUPERSMARTMATCH V2 - TESTS AVANCÉS           ║${NC}"
echo -e "${CYAN}║                      Version 2.0 Enhanced                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

info "Démarrage des tests - $(date)"

# ═══════════════════════════════════════════════════════════════════
# 1. TESTS DE SANTÉ DES SERVICES
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🏥 === TESTS DE SANTÉ DES SERVICES ===${NC}"

test_endpoint "SuperSmartMatch V2 Health" "GET" "$SSM_V2_URL/health"
test_endpoint "Nexten Matcher Health" "GET" "$NEXTEN_URL/health"
test_endpoint "SuperSmartMatch V1 Health" "GET" "$SSM_V1_URL/health"

# Vérification des ports
info "Vérification des ports actifs..."
if netstat -tlnp 2>/dev/null | grep -q ":5070"; then
    success "Port 5070 (SuperSmartMatch V2) actif"
else
    error "Port 5070 (SuperSmartMatch V2) non actif"
fi

if netstat -tlnp 2>/dev/null | grep -q ":5052"; then
    success "Port 5052 (Nexten Matcher) actif"
else
    warning "Port 5052 (Nexten Matcher) non actif - Tests Nexten seront ignorés"
fi

if netstat -tlnp 2>/dev/null | grep -q ":5062"; then
    success "Port 5062 (SuperSmartMatch V1) actif"
else
    warning "Port 5062 (SuperSmartMatch V1) non actif - Fallback limité"
fi

# ═══════════════════════════════════════════════════════════════════
# 2. TESTS API V2 NATIVE
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🔥 === TESTS API V2 NATIVE ===${NC}"

# Test API V2 basique
basic_v2_data='{
  "candidate": {
    "name": "Jean Dupont", 
    "technical_skills": [
      {"name": "Python", "level": "Advanced", "years": 3}
    ]
  },
  "offers": [
    {
      "id": "job-001",
      "title": "Développeur Python",
      "required_skills": ["Python", "Django"]
    }
  ],
  "algorithm": "auto"
}'

test_endpoint "API V2 - Test basique" "POST" "$SSM_V2_URL/api/v2/match" "$basic_v2_data"

# Test API V2 avec questionnaire (devrait sélectionner Nexten)
nexten_priority_data='{
  "candidate": {
    "name": "Alice Expert",
    "technical_skills": [
      {"name": "Python", "level": "Expert", "years": 6},
      {"name": "Machine Learning", "level": "Advanced", "years": 4}
    ]
  },
  "candidate_questionnaire": {
    "work_style": "analytical",
    "culture_preferences": "data_driven",
    "remote_preference": "hybrid"
  },
  "offers": [
    {
      "id": "ml-engineer-001",
      "title": "Senior ML Engineer", 
      "required_skills": ["Python", "TensorFlow", "AWS"]
    }
  ],
  "algorithm": "auto"
}'

test_endpoint "API V2 - Sélection Nexten (questionnaire)" "POST" "$SSM_V2_URL/api/v2/match" "$nexten_priority_data"

# Test géolocalisation (devrait sélectionner Smart Match)
geo_data='{
  "candidate": {
    "name": "Pierre Mobile",
    "technical_skills": ["JavaScript", "React"],
    "localisation": "Lyon",
    "mobility": true
  },
  "offers": [
    {
      "id": "js-paris-001",
      "title": "Développeur React",
      "localisation": "Paris",
      "required_skills": ["JavaScript", "React"]
    }
  ],
  "algorithm": "auto"
}'

test_endpoint "API V2 - Sélection Smart Match (géo)" "POST" "$SSM_V2_URL/api/v2/match" "$geo_data"

# Test profil senior (devrait sélectionner Enhanced)
senior_data='{
  "candidate": {
    "name": "Philippe Senior",
    "technical_skills": ["Java", "Architecture", "Leadership"],
    "experiences": [
      {"duration_months": 48, "title": "Tech Lead", "company": "TechCorp"},
      {"duration_months": 36, "title": "Senior Architect", "company": "DevCorp"}
    ]
  },
  "offers": [
    {
      "id": "architect-001",
      "title": "Solution Architect",
      "required_skills": ["Java", "Architecture"],
      "level": "Senior"
    }
  ],
  "algorithm": "auto"
}'

test_endpoint "API V2 - Sélection Enhanced (senior)" "POST" "$SSM_V2_URL/api/v2/match" "$senior_data"

# ═══════════════════════════════════════════════════════════════════
# 3. TESTS COMPATIBILITÉ V1
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🔄 === TESTS COMPATIBILITÉ V1 ===${NC}"

# Test format V1 classique (sans /api/v2/)
v1_compat_data='{
  "candidate": {
    "name": "Test Compatibility",
    "technical_skills": ["JavaScript", "Node.js"]
  },
  "offers": [
    {
      "id": "js-job-001",
      "title": "Développeur Node.js",
      "required_skills": ["JavaScript", "Node.js"]
    }
  ]
}'

test_endpoint "Compatibilité V1 - Endpoint /match" "POST" "$SSM_V2_URL/match" "$v1_compat_data"

# Test format offers vs jobs
jobs_format_data='{
  "candidate": {
    "name": "Test Jobs Format",
    "technical_skills": ["Python"]
  },
  "jobs": [
    {
      "id": "python-job-001",
      "title": "Développeur Python"
    }
  ]
}'

test_endpoint "Compatibilité V1 - Format jobs" "POST" "$SSM_V2_URL/match" "$jobs_format_data"

# ═══════════════════════════════════════════════════════════════════
# 4. TESTS DE PERFORMANCE
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}⚡ === TESTS DE PERFORMANCE ===${NC}"

# Test performance API V2
perf_data='{
  "candidate": {"name": "Perf Test", "technical_skills": ["Python"]},
  "offers": [{"id": "perf-001", "title": "Test Performance"}],
  "algorithm": "auto"
}'

test_performance "Performance API V2" "$SSM_V2_URL/api/v2/match" "$perf_data" 500

# Test performance charge légère (5 requêtes simultanées)
info "Test de charge légère (5 requêtes)..."
pids=()
for i in {1..5}; do
    (
        curl -s -X POST "$SSM_V2_URL/api/v2/match" \
            -H "Content-Type: application/json" \
            -d '{"candidate":{"name":"Load Test '${i}'"},"offers":[{"id":"load-'${i}'"}]}' \
            >/dev/null
    ) &
    pids+=($!)
done

# Attendre la fin de tous les processus
for pid in "${pids[@]}"; do
    wait $pid
done

success "Test de charge légère terminé"

# ═══════════════════════════════════════════════════════════════════
# 5. TESTS ENDPOINTS SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🔧 === TESTS ENDPOINTS SPÉCIALISÉS ===${NC}"

# Test métriques
test_endpoint "Métriques Prometheus" "GET" "$SSM_V2_URL/metrics"

# Test liste algorithmes
test_endpoint "Liste des algorithmes" "GET" "$SSM_V2_URL/api/v2/algorithms"

# Test statistiques
test_endpoint "Statistiques du service" "GET" "$SSM_V2_URL/stats"

# Test info service
test_endpoint "Informations du service" "GET" "$SSM_V2_URL/info"

# ═══════════════════════════════════════════════════════════════════
# 6. TESTS D'ERREURS ET CAS LIMITES
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🚨 === TESTS D'ERREURS ET CAS LIMITES ===${NC}"

# Test données invalides
test_endpoint "Erreur - JSON invalide" "POST" "$SSM_V2_URL/api/v2/match" "invalid-json" 400

# Test données manquantes
test_endpoint "Erreur - Données manquantes" "POST" "$SSM_V2_URL/api/v2/match" '{"candidate":{"name":"Test"}}' 400

# Test algorithme inexistant
invalid_algo_data='{
  "candidate": {"name": "Test"},
  "offers": [{"id": "test"}],
  "algorithm": "nonexistent_algo"
}'

test_endpoint "Erreur - Algorithme inexistant" "POST" "$SSM_V2_URL/api/v2/match" "$invalid_algo_data" 400

# ═══════════════════════════════════════════════════════════════════
# 7. TESTS ALGORITHMES SPÉCIFIQUES
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🧠 === TESTS ALGORITHMES SPÉCIFIQUES ===${NC}"

# Test forçage algorithme specific
for algo in "basic" "smart" "enhanced" "semantic"; do
    algo_data='{
      "candidate": {"name": "Test '${algo^}'", "technical_skills": ["Python"]},
      "offers": [{"id": "test-'$algo'", "title": "Test '$algo'"}],
      "algorithm": "'$algo'"
    }'
    
    test_endpoint "Algorithme forcé - $algo" "POST" "$SSM_V2_URL/api/v2/match" "$algo_data"
done

# ═══════════════════════════════════════════════════════════════════
# 8. VALIDATION DES RÉPONSES
# ═══════════════════════════════════════════════════════════════════

echo
log "${PURPLE}🔍 === VALIDATION STRUCTURE RÉPONSES ===${NC}"

info "Validation détaillée de la structure de réponse..."

response=$(curl -s -X POST "$SSM_V2_URL/api/v2/match" \
    -H "Content-Type: application/json" \
    -d '{"candidate":{"name":"Validation Test"},"offers":[{"id":"val-001"}],"algorithm":"auto"}')

if echo "$response" | jq . >/dev/null 2>&1; then
    # Vérifications des champs obligatoires
    if echo "$response" | jq -e '.matches' >/dev/null 2>&1; then
        success "Champ 'matches' présent"
    else
        error "Champ 'matches' manquant"
    fi
    
    if echo "$response" | jq -e '.algorithm_used' >/dev/null 2>&1; then
        algo_used=$(echo "$response" | jq -r '.algorithm_used')
        success "Algorithme utilisé: $algo_used"
    else
        error "Champ 'algorithm_used' manquant"
    fi
    
    if echo "$response" | jq -e '.processing_time_ms' >/dev/null 2>&1; then
        time_ms=$(echo "$response" | jq -r '.processing_time_ms')
        success "Temps de traitement: ${time_ms}ms"
    else
        warning "Champ 'processing_time_ms' manquant"
    fi
    
    if echo "$response" | jq -e '.metadata' >/dev/null 2>&1; then
        success "Métadonnées présentes"
    else
        warning "Champ 'metadata' manquant"
    fi
else
    error "Réponse JSON invalide pour validation"
fi

# ═══════════════════════════════════════════════════════════════════
# 9. RAPPORT FINAL
# ═══════════════════════════════════════════════════════════════════

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo
log "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
log "${CYAN}║                    📊 RAPPORT FINAL                         ║${NC}"
log "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"

echo
log "${GREEN}✅ Tests réussis: $PASSED_TESTS${NC}"
log "${RED}❌ Tests échoués: $FAILED_TESTS${NC}"
log "${BLUE}📊 Total tests: $TOTAL_TESTS${NC}"
log "${PURPLE}⏱️  Durée totale: ${DURATION}s${NC}"

# Calcul du taux de réussite
if [[ $TOTAL_TESTS -gt 0 ]]; then
    success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    log "${CYAN}📈 Taux de réussite: ${success_rate}%${NC}"
    
    if [[ $success_rate -ge 90 ]]; then
        echo
        log "${GREEN}🎉 EXCELLENT! SuperSmartMatch V2 fonctionne parfaitement!${NC}"
        exit 0
    elif [[ $success_rate -ge 75 ]]; then
        echo
        log "${YELLOW}⚠️  BON! Quelques problèmes mineurs détectés${NC}"
        exit 1
    else
        echo
        log "${RED}🚨 PROBLÈMES DÉTECTÉS! Vérifiez la configuration${NC}"
        exit 2
    fi
else
    log "${RED}❌ Aucun test exécuté${NC}"
    exit 3
fi
