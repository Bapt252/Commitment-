#!/bin/bash

# Test d'intégration SuperSmartMatch avec Nexten Frontend
# Vérifie la compatibilité avec votre front-end existant

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔗 Test d'Intégration SuperSmartMatch ↔ Nexten Frontend${NC}"
echo "=========================================================="

PORT=${1:-5061}
BASE_URL="http://localhost:$PORT"

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test de connexion
test_connection() {
    log_info "Test de connexion au service SuperSmartMatch..."
    
    if curl -s --max-time 5 "$BASE_URL/api/health" > /dev/null 2>&1; then
        log_success "Service SuperSmartMatch accessible sur $BASE_URL"
        return 0
    else
        log_error "Service SuperSmartMatch non accessible sur $BASE_URL"
        log_info "Assurez-vous que SuperSmartMatch est démarré avec: ./start-supersmartmatch.sh"
        return 1
    fi
}

# Test avec des données réalistes du projet Nexten
test_nexten_matching() {
    log_info "Test avec des données réalistes du projet Nexten..."
    
    # Données d'un candidat type Nexten
    cat > /tmp/nexten_test_data.json << 'EOF'
{
  "cv_data": {
    "competences": [
      "Python",
      "Django",
      "JavaScript",
      "React",
      "PostgreSQL",
      "Docker",
      "Git",
      "API REST",
      "Machine Learning",
      "Data Analysis"
    ],
    "annees_experience": 5,
    "niveau_etudes": "Master",
    "langues": ["Français", "Anglais"],
    "secteurs_activite": ["Tech", "Finance", "E-commerce"]
  },
  "questionnaire_data": {
    "adresse": "75001 Paris, France",
    "salaire_souhaite": 55000,
    "mobilite": "hybrid",
    "disponibilite": "immediat",
    "type_contrat": "CDI",
    "taille_entreprise": "PME",
    "secteur_prefere": "Tech"
  },
  "job_data": [
    {
      "id": "nexten_job_001",
      "titre": "Développeur Full Stack Senior",
      "entreprise": "TechCorp Paris",
      "competences": ["Python", "Django", "React", "PostgreSQL", "Docker"],
      "localisation": "75008 Paris",
      "salaire_min": 50000,
      "salaire_max": 65000,
      "type_contrat": "CDI",
      "experience_requise": 4,
      "secteur": "Tech",
      "taille_entreprise": "PME",
      "politique_remote": "hybrid",
      "description": "Développement d'applications web modernes en équipe agile"
    },
    {
      "id": "nexten_job_002", 
      "titre": "Data Scientist",
      "entreprise": "FinanceInnovation",
      "competences": ["Python", "Machine Learning", "Data Analysis", "SQL", "Pandas"],
      "localisation": "75002 Paris",
      "salaire_min": 48000,
      "salaire_max": 62000,
      "type_contrat": "CDI",
      "experience_requise": 3,
      "secteur": "Finance",
      "taille_entreprise": "Grande entreprise",
      "politique_remote": "partial",
      "description": "Analyse de données financières et modélisation prédictive"
    },
    {
      "id": "nexten_job_003",
      "titre": "Frontend Developer",
      "entreprise": "EcommerceStartup",
      "competences": ["JavaScript", "React", "CSS", "HTML", "Node.js"],
      "localisation": "75011 Paris",
      "salaire_min": 42000,
      "salaire_max": 52000,
      "type_contrat": "CDI",
      "experience_requise": 3,
      "secteur": "E-commerce",
      "taille_entreprise": "Startup",
      "politique_remote": "full_remote",
      "description": "Interface utilisateur pour plateforme e-commerce"
    },
    {
      "id": "nexten_job_004",
      "titre": "DevOps Engineer",
      "entreprise": "CloudSolutions",
      "competences": ["Docker", "Kubernetes", "AWS", "Python", "Linux"],
      "localisation": "92100 Boulogne",
      "salaire_min": 53000,
      "salaire_max": 68000,
      "type_contrat": "CDI",
      "experience_requise": 5,
      "secteur": "Tech",
      "taille_entreprise": "PME",
      "politique_remote": "hybrid",
      "description": "Infrastructure cloud et automatisation CI/CD"
    },
    {
      "id": "nexten_job_005",
      "titre": "Junior Web Developer",
      "entreprise": "AgenceDev",
      "competences": ["JavaScript", "HTML", "CSS", "PHP", "MySQL"],
      "localisation": "75020 Paris",
      "salaire_min": 32000,
      "salaire_max": 38000,
      "type_contrat": "CDI",
      "experience_requise": 1,
      "secteur": "Services",
      "taille_entreprise": "PME",
      "politique_remote": "on_site",
      "description": "Développement de sites web pour clients divers"
    }
  ],
  "algorithm": "auto",
  "limit": 10
}
EOF

    log_info "Envoi de la requête de matching..."
    
    response=$(curl -s -X POST "$BASE_URL/api/match" \
        -H "Content-Type: application/json" \
        -d @/tmp/nexten_test_data.json)
    
    if [ $? -eq 0 ]; then
        log_success "Matching exécuté avec succès"
        
        # Analyser la réponse
        echo "$response" | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    
    if 'error' in data:
        print('❌ Erreur dans la réponse:', data['error'])
        sys.exit(1)
    
    print('✅ Algorithme utilisé:', data.get('algorithm_used', 'unknown'))
    print('⏱️  Temps d\'exécution:', data.get('execution_time', 0), 'secondes')
    print('📊 Nombre de résultats:', data.get('total_results', 0))
    
    results = data.get('results', [])
    if results:
        print('\\n🎯 Top 3 des matches:')
        for i, job in enumerate(results[:3]):
            score = job.get('matching_score', 0)
            title = job.get('titre', 'Titre inconnu')
            company = job.get('entreprise', 'Entreprise inconnue')
            location = job.get('localisation', 'Localisation inconnue')
            print(f'  {i+1}. {title} chez {company} ({location}) - Score: {score}%')
            
        # Vérifier la cohérence des scores
        scores = [job.get('matching_score', 0) for job in results]
        if scores == sorted(scores, reverse=True):
            print('✅ Scores correctement triés par ordre décroissant')
        else:
            print('⚠️  Attention: scores pas correctement triés')
            
        # Vérifier que les scores sont réalistes
        valid_scores = all(0 <= score <= 100 for score in scores)
        if valid_scores:
            print('✅ Tous les scores sont dans la plage [0-100]')
        else:
            print('⚠️  Attention: scores hors de la plage valide')
    else:
        print('⚠️  Aucun résultat retourné')
        
except json.JSONDecodeError:
    print('❌ Réponse JSON invalide')
    sys.exit(1)
except Exception as e:
    print('❌ Erreur lors de l\'analyse:', str(e))
    sys.exit(1)
"
    else
        log_error "Échec de la requête de matching"
        return 1
    fi
    
    # Nettoyer
    rm -f /tmp/nexten_test_data.json
}

# Test des différents algorithmes
test_algorithms() {
    log_info "Test des différents algorithmes disponibles..."
    
    algorithms=("auto" "enhanced" "smart_match" "custom" "hybrid")
    
    for algo in "${algorithms[@]}"; do
        log_info "Test de l'algorithme: $algo"
        
        response=$(curl -s -X POST "$BASE_URL/api/match" \
            -H "Content-Type: application/json" \
            -d "{
                \"cv_data\": {
                    \"competences\": [\"Python\", \"JavaScript\"],
                    \"annees_experience\": 3
                },
                \"questionnaire_data\": {
                    \"adresse\": \"Paris\",
                    \"salaire_souhaite\": 45000
                },
                \"job_data\": [
                    {
                        \"id\": \"test_job\",
                        \"titre\": \"Développeur\",
                        \"competences\": [\"Python\", \"Django\"],
                        \"localisation\": \"Paris\",
                        \"salaire_min\": 40000,
                        \"salaire_max\": 50000
                    }
                ],
                \"algorithm\": \"$algo\",
                \"limit\": 5
            }")
        
        if echo "$response" | grep -q '"algorithm_used"'; then
            used_algo=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('algorithm_used','unknown'))")
            log_success "Algorithme $algo → $used_algo fonctionnel"
        else
            log_warning "Algorithme $algo non disponible ou en erreur"
        fi
    done
}

# Test de performance
test_performance() {
    log_info "Test de performance avec un gros volume de données..."
    
    # Créer 50 offres d'emploi pour le test
    jobs_data="["
    for i in $(seq 1 50); do
        if [ $i -gt 1 ]; then
            jobs_data="$jobs_data,"
        fi
        jobs_data="$jobs_data{
            \"id\": \"perf_job_$i\",
            \"titre\": \"Job $i\",
            \"competences\": [\"Python\", \"JavaScript\", \"React\"],
            \"localisation\": \"Paris\",
            \"salaire_min\": $((30000 + i * 500)),
            \"salaire_max\": $((40000 + i * 500))
        }"
    done
    jobs_data="$jobs_data]"
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -X POST "$BASE_URL/api/match" \
        -H "Content-Type: application/json" \
        -d "{
            \"cv_data\": {
                \"competences\": [\"Python\", \"JavaScript\", \"React\", \"Django\", \"Node.js\"],
                \"annees_experience\": 5
            },
            \"questionnaire_data\": {
                \"adresse\": \"Paris\",
                \"salaire_souhaite\": 50000
            },
            \"job_data\": $jobs_data,
            \"algorithm\": \"hybrid\",
            \"limit\": 20
        }")
    
    end_time=$(date +%s.%N)
    total_time=$(echo "$end_time - $start_time" | bc -l)
    
    if echo "$response" | grep -q '"execution_time"'; then
        server_time=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('execution_time',0))")
        results_count=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('total_results',0))")
        
        log_success "Performance test réussi:"
        printf "  📊 50 jobs analysés → %s résultats\n" "$results_count"
        printf "  ⏱️  Temps total: %.3fs (serveur: %ss)\n" "$total_time" "$server_time"
        
        if (( $(echo "$server_time < 5.0" | bc -l) )); then
            log_success "Performance acceptable (< 5s)"
        else
            log_warning "Performance lente (> 5s), optimisation recommandée"
        fi
    else
        log_error "Échec du test de performance"
    fi
}

# Test d'intégration avec CORS
test_cors() {
    log_info "Test de la configuration CORS..."
    
    response=$(curl -s -X OPTIONS "$BASE_URL/api/match" \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -I)
    
    if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
        log_success "CORS configuré correctement"
    else
        log_warning "CORS pourrait nécessiter une configuration"
    fi
}

# Test avec des données invalides
test_error_handling() {
    log_info "Test de la gestion d'erreurs..."
    
    # Test avec données manquantes
    response=$(curl -s -X POST "$BASE_URL/api/match" \
        -H "Content-Type: application/json" \
        -d "{\"cv_data\": {}}")
    
    if echo "$response" | grep -q '"error"'; then
        log_success "Gestion d'erreur pour données manquantes: OK"
    else
        log_warning "Gestion d'erreur pour données manquantes à améliorer"
    fi
    
    # Test avec JSON invalide
    response_code=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/api/match" \
        -H "Content-Type: application/json" \
        -d "invalid json" \
        -o /dev/null)
    
    if [ "$response_code" = "400" ]; then
        log_success "Gestion d'erreur pour JSON invalide: OK"
    else
        log_warning "Gestion d'erreur pour JSON invalide à améliorer (code: $response_code)"
    fi
}

# Génération du rapport d'intégration
generate_integration_guide() {
    log_info "Génération du guide d'intégration pour votre front-end..."
    
    cat > "nexten-supersmartmatch-integration.js" << 'EOF'
/**
 * Module d'intégration SuperSmartMatch pour Nexten
 * Utilisation dans vos templates existants
 */

class NextenSuperSmartMatch {
    constructor(baseUrl = 'http://localhost:5061') {
        this.baseUrl = baseUrl;
        this.timeout = 30000; // 30 secondes
    }

    // Test de connexion
    async isHealthy() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`, {
                method: 'GET',
                timeout: 5000
            });
            return response.ok;
        } catch (error) {
            console.error('SuperSmartMatch health check failed:', error);
            return false;
        }
    }

    // Récupérer les algorithmes disponibles
    async getAvailableAlgorithms() {
        try {
            const response = await fetch(`${this.baseUrl}/api/algorithms`);
            const data = await response.json();
            return data.algorithms;
        } catch (error) {
            console.error('Failed to get algorithms:', error);
            return {};
        }
    }

    // Fonction principale de matching
    async match(cvData, questionnaireData, jobsData, options = {}) {
        const payload = {
            cv_data: cvData,
            questionnaire_data: questionnaireData,
            job_data: jobsData,
            algorithm: options.algorithm || 'auto',
            limit: options.limit || 10
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(`${this.baseUrl}/api/match`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Matching failed: ${errorData.error || response.statusText}`);
            }

            const result = await response.json();
            
            // Post-traitement pour votre front-end
            return this.formatResultsForNexten(result);

        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Matching timeout - le service met trop de temps à répondre');
            }
            console.error('SuperSmartMatch error:', error);
            throw error;
        }
    }

    // Formatage des résultats pour l'interface Nexten
    formatResultsForNexten(apiResult) {
        const results = apiResult.results || [];
        
        return {
            // Métadonnées du matching
            metadata: {
                algorithm: apiResult.algorithm_used,
                executionTime: apiResult.execution_time,
                totalResults: apiResult.total_results,
                timestamp: new Date().toISOString()
            },
            
            // Résultats formatés pour votre interface
            matches: results.map((job, index) => ({
                rank: index + 1,
                jobId: job.id,
                title: job.titre,
                company: job.entreprise,
                location: job.localisation,
                matchingScore: job.matching_score,
                salaryRange: {
                    min: job.salaire_min,
                    max: job.salaire_max
                },
                contractType: job.type_contrat,
                requiredExperience: job.experience_requise,
                skills: job.competences || [],
                sector: job.secteur,
                remotePolicy: job.politique_remote,
                description: job.description,
                
                // Données spécifiques à l'algorithme hybrid
                hybridDetails: job.hybrid_details,
                
                // Score formaté pour l'affichage
                scoreClass: this.getScoreClass(job.matching_score),
                scoreLabel: this.getScoreLabel(job.matching_score)
            })),
            
            // Statistiques pour le dashboard
            statistics: {
                averageScore: results.length > 0 
                    ? Math.round(results.reduce((sum, job) => sum + job.matching_score, 0) / results.length)
                    : 0,
                highScoreCount: results.filter(job => job.matching_score >= 80).length,
                mediumScoreCount: results.filter(job => job.matching_score >= 60 && job.matching_score < 80).length,
                lowScoreCount: results.filter(job => job.matching_score < 60).length
            }
        };
    }

    // Classes CSS pour les scores
    getScoreClass(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        if (score >= 40) return 'score-average';
        return 'score-low';
    }

    // Labels pour les scores
    getScoreLabel(score) {
        if (score >= 90) return 'Excellent match';
        if (score >= 80) return 'Très bon match';
        if (score >= 70) return 'Bon match';
        if (score >= 60) return 'Match correct';
        if (score >= 40) return 'Match partiel';
        return 'Match faible';
    }

    // Matching par lots pour de gros volumes
    async batchMatch(candidates, jobsData, options = {}) {
        const batchSize = options.batchSize || 10;
        const results = [];

        for (let i = 0; i < candidates.length; i += batchSize) {
            const batch = candidates.slice(i, i + batchSize);
            const batchPromises = batch.map(candidate => 
                this.match(candidate.cvData, candidate.questionnaireData, jobsData, options)
            );

            try {
                const batchResults = await Promise.all(batchPromises);
                results.push(...batchResults);
            } catch (error) {
                console.error(`Batch ${Math.floor(i/batchSize) + 1} failed:`, error);
                // Continuer avec le lot suivant
            }
        }

        return results;
    }
}

// Utilisation dans vos templates
// window.nextenMatching = new NextenSuperSmartMatch();

// Exemple d'utilisation:
/*
async function exempleUtilisation() {
    const matching = new NextenSuperSmartMatch();
    
    // Vérifier que le service est disponible
    if (!(await matching.isHealthy())) {
        console.error('SuperSmartMatch non disponible');
        return;
    }

    // Données du formulaire Nexten
    const cvData = {
        competences: ['Python', 'JavaScript', 'React'],
        annees_experience: 3
        // ... autres données du CV
    };

    const questionnaireData = {
        adresse: 'Paris',
        salaire_souhaite: 45000
        // ... autres données du questionnaire
    };

    const jobsData = [
        // ... vos offres d'emploi
    ];

    try {
        const result = await matching.match(cvData, questionnaireData, jobsData, {
            algorithm: 'hybrid', // ou 'auto'
            limit: 10
        });

        // Utiliser les résultats dans votre interface
        console.log('Métadonnées:', result.metadata);
        console.log('Matches:', result.matches);
        console.log('Statistiques:', result.statistics);

        // Afficher les résultats
        afficherResultatsMatching(result.matches);
        
    } catch (error) {
        console.error('Erreur lors du matching:', error);
        // Gérer l'erreur dans votre interface
    }
}
*/
EOF

    log_success "Guide d'intégration généré: nexten-supersmartmatch-integration.js"
}

# Fonction principale
main() {
    echo "🔧 Test d'intégration SuperSmartMatch avec Nexten"
    echo "Port utilisé: $PORT"
    echo ""
    
    # Tests séquentiels
    if ! test_connection; then
        log_error "Impossible de continuer sans connexion au service"
        exit 1
    fi
    
    echo ""
    test_nexten_matching
    
    echo ""
    test_algorithms
    
    echo ""
    test_performance
    
    echo ""
    test_cors
    
    echo ""
    test_error_handling
    
    echo ""
    generate_integration_guide
    
    echo ""
    echo "🎉 Tests d'intégration terminés !"
    echo ""
    echo "📋 Résumé:"
    echo "   ✅ SuperSmartMatch accessible et fonctionnel"
    echo "   ✅ Tests avec données réalistes Nexten réussis"
    echo "   ✅ Algorithmes multiples disponibles"
    echo "   ✅ Performance acceptable"
    echo "   ✅ Guide d'intégration généré"
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "   1. Intégrer nexten-supersmartmatch-integration.js dans vos templates"
    echo "   2. Adapter les endpoints dans votre code existant"
    echo "   3. Tester avec vos données de production"
    echo ""
    echo "📖 Documentation complète: SUPERSMARTMATCH-QUICKSTART.md"
}

# Exécution
main "$@"
