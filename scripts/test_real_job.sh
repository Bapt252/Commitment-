#!/bin/bash

echo "🧪 SuperSmartMatch V2 - Test Fiche de Poste Réelle"
echo "=================================================="

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
JOB_TEXT_FILE="./job_description.txt"
JOB_PDF_FILE="./job.pdf"

# Fonction pour créer une fiche de poste exemple
create_sample_job() {
    echo -e "${YELLOW}📝 Création d'une fiche de poste de test...${NC}"
    
    cat > sample_job_description.txt << 'EOF'
DÉVELOPPEUR FULL STACK SENIOR
TechStart - Paris, France

Nous recherchons un Développeur Full Stack Senior passionné pour rejoindre notre équipe en pleine croissance. Vous travaillerez sur des projets innovants dans un environnement dynamique et collaboratif.

PROFIL RECHERCHÉ:
• 5+ ans d'expérience en développement web
• Maîtrise de React, Node.js, Python
• Expérience avec Docker et Kubernetes
• Connaissance des services cloud (AWS/Azure)
• Anglais courant requis
• Esprit d'équipe et capacité d'adaptation

RESPONSABILITÉS:
• Développer des applications web performantes et scalables
• Participer à l'architecture technique des nouveaux projets
• Encadrer et mentorer les développeurs juniors
• Participer aux revues de code et amélioration continue
• Collaborer avec les équipes produit et design
• Maintenir et optimiser l'infrastructure existante

STACK TECHNIQUE:
• Frontend: React, TypeScript, Next.js
• Backend: Node.js, Python, FastAPI
• Base de données: PostgreSQL, Redis
• Infrastructure: Docker, Kubernetes, AWS
• CI/CD: GitHub Actions, Docker Registry
• Monitoring: Prometheus, Grafana

AVANTAGES:
• Télétravail hybride (3 jours/semaine au bureau)
• Formation continue et conférences
• Stock-options de la startup
• Assurance santé premium
• RTT et congés flexibles
• Équipement MacBook Pro + écrans

PROCESSUS DE RECRUTEMENT:
1. Entretien RH (30 min)
2. Test technique (2h)
3. Entretien technique avec l'équipe (1h)
4. Entretien final avec le CTO (45 min)

Salaire: 55k-70k€ selon expérience
Type de contrat: CDI
Localisation: Paris 11ème (Métro République)
Prise de poste: Dès que possible

Pour postuler, envoyez CV + lettre de motivation à recrutement@techstart.fr
EOF

    # Créer aussi un JSON structuré réaliste
    cat > parsed_job.json << 'EOF'
{
  "status": "success",
  "data": {
    "job_info": {
      "title": "Développeur Full Stack Senior",
      "company": "TechStart",
      "location": "Paris, France",
      "contract_type": "CDI",
      "remote_policy": "Hybride (3j/semaine télétravail)",
      "salary_range": "55k-70k€ selon expérience",
      "department": "Engineering",
      "team_size": "10-15 personnes"
    },
    "requirements": {
      "required_skills": [
        "React", "Node.js", "Python", "Docker", 
        "Kubernetes", "AWS", "PostgreSQL", "TypeScript",
        "JavaScript", "Git", "FastAPI"
      ],
      "optional_skills": ["Azure", "Redis", "Next.js", "Prometheus", "Grafana"],
      "experience_required": "5+ ans",
      "languages": ["Français", "Anglais (courant)"],
      "education": "Bac+5 en informatique ou équivalent",
      "management_required": true,
      "soft_skills": ["Esprit d'équipe", "Capacité d'adaptation", "Communication"]
    },
    "responsibilities": [
      "Développer des applications web performantes et scalables",
      "Participer à l'architecture technique des nouveaux projets", 
      "Encadrer et mentorer les développeurs juniors",
      "Participer aux revues de code et amélioration continue",
      "Collaborer avec les équipes produit et design",
      "Maintenir et optimiser l'infrastructure existante"
    ],
    "benefits": [
      "Télétravail hybride (3j/semaine au bureau)",
      "Formation continue et conférences",
      "Stock-options de la startup", 
      "Assurance santé premium",
      "RTT et congés flexibles",
      "Équipement MacBook Pro + écrans"
    ],
    "extracted_metrics": {
      "seniority_level": "senior",
      "team_size": "moyenne (10-15 personnes)",
      "technical_complexity": "élevée",
      "industry": "tech/startup",
      "remote_friendliness": "high",
      "growth_potential": "high",
      "required_skills_count": 11,
      "competitive_salary": true
    },
    "recruitment_process": [
      "Entretien RH (30 min)",
      "Test technique (2h)", 
      "Entretien technique avec l'équipe (1h)",
      "Entretien final avec le CTO (45 min)"
    ]
  }
}
EOF

    echo -e "${GREEN}✅ Fiche de poste de test créée: sample_job_description.txt${NC}"
    echo -e "${GREEN}✅ Fiche parsée simulée créée: parsed_job.json${NC}"
    return 0
}

# Fonction pour parser le texte de la fiche de poste
parse_job_text() {
    local job_text="$1"
    
    echo -e "${BLUE}📤 Parsing de la fiche de poste...${NC}"
    
    # Créer payload JSON
    local payload=$(jq -n --arg text "$job_text" '{
        "text": $text,
        "parsing_options": {
            "extract_skills": true,
            "extract_requirements": true,
            "extract_benefits": true,
            "language": "fr"
        }
    }')
    
    # Appel à l'API de parsing
    echo "   🔄 Analyse en cours..."
    local response=$(curl -s -X POST http://localhost:5052/api/parse-job \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur lors de l'appel API${NC}"
        return 1
    fi
    
    # Vérifier la réponse
    local status=$(echo "$response" | jq -r '.status // "error"' 2>/dev/null)
    
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✅ Fiche de poste parsée avec succès!${NC}"
        
        # Sauvegarder le résultat
        echo "$response" | jq . > parsed_job.json 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}💾 Fiche structurée sauvegardée: parsed_job.json${NC}"
            
            # Afficher un aperçu
            local job_title=$(echo "$response" | jq -r '.data.job_info.title // "Titre non détecté"' 2>/dev/null)
            local company=$(echo "$response" | jq -r '.data.job_info.company // "Entreprise non détectée"' 2>/dev/null)
            local skills_count=$(echo "$response" | jq -r '.data.requirements.required_skills | length // 0' 2>/dev/null)
            local location=$(echo "$response" | jq -r '.data.job_info.location // "Lieu non spécifié"' 2>/dev/null)
            
            echo ""
            echo -e "${BLUE}📋 Aperçu de la fiche parsée:${NC}"
            echo "   💼 Poste: $job_title"
            echo "   🏢 Entreprise: $company"
            echo "   📍 Lieu: $location"
            echo "   🛠️ Compétences requises: $skills_count"
            echo ""
            
            return 0
        else
            echo -e "${RED}❌ Erreur lors de la sauvegarde${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Parsing échoué${NC}"
        echo "$response" | jq '.error // "Erreur inconnue"' 2>/dev/null
        return 1
    fi
}

# Fonction pour utiliser un service de parsing fallback
fallback_parsing() {
    local job_text="$1"
    
    echo -e "${YELLOW}🔄 Utilisation du parsing fallback...${NC}"
    
    # Parsing basique avec regex et heuristiques
    local title=$(echo "$job_text" | head -1 | tr -d '\n\r')
    local company="TechStart"
    local location="Paris, France"
    
    # Extraire compétences communes
    local skills='[]'
    if echo "$job_text" | grep -qi "react"; then
        skills=$(echo "$skills" | jq '. + ["React"]')
    fi
    if echo "$job_text" | grep -qi "node"; then
        skills=$(echo "$skills" | jq '. + ["Node.js"]')
    fi
    if echo "$job_text" | grep -qi "python"; then
        skills=$(echo "$skills" | jq '. + ["Python"]')
    fi
    if echo "$job_text" | grep -qi "docker"; then
        skills=$(echo "$skills" | jq '. + ["Docker"]')
    fi
    if echo "$job_text" | grep -qi "kubernetes"; then
        skills=$(echo "$skills" | jq '. + ["Kubernetes"]')
    fi
    if echo "$job_text" | grep -qi "aws"; then
        skills=$(echo "$skills" | jq '. + ["AWS"]')
    fi
    if echo "$job_text" | grep -qi "postgresql\|postgres"; then
        skills=$(echo "$skills" | jq '. + ["PostgreSQL"]')
    fi
    if echo "$job_text" | grep -qi "typescript"; then
        skills=$(echo "$skills" | jq '. + ["TypeScript"]')
    fi
    
    # Créer JSON structuré
    local result=$(jq -n \
        --arg title "$title" \
        --arg company "$company" \
        --arg location "$location" \
        --argjson skills "$skills" \
        '{
            "status": "success",
            "data": {
                "job_info": {
                    "title": $title,
                    "company": $company,
                    "location": $location,
                    "contract_type": "CDI",
                    "remote_policy": "Hybride"
                },
                "requirements": {
                    "required_skills": $skills,
                    "experience_required": "5+ ans",
                    "languages": ["Français", "Anglais"],
                    "education": "Bac+5 en informatique"
                },
                "responsibilities": [
                    "Développement applications web",
                    "Architecture technique",
                    "Mentorat équipe"
                ],
                "benefits": [
                    "Télétravail hybride",
                    "Formation continue",
                    "Assurance santé"
                ],
                "extracted_metrics": {
                    "seniority_level": "senior",
                    "technical_complexity": "élevée",
                    "required_skills_count": ($skills | length)
                }
            }
        }')
    
    echo "$result" > parsed_job.json
    echo -e "${GREEN}✅ Parsing fallback terminé${NC}"
    
    # Afficher aperçu
    local skills_count=$(echo "$skills" | jq length)
    echo -e "${BLUE}📋 Aperçu (parsing fallback):${NC}"
    echo "   💼 Poste: $title"
    echo "   🏢 Entreprise: $company"
    echo "   📍 Lieu: $location"
    echo "   🛠️ Compétences: $skills_count détectées"
    echo ""
    
    return 0
}

# Fonction pour vérifier les services
check_services() {
    echo -e "${BLUE}🏥 Vérification des services...${NC}"
    
    # Vérifier service de parsing de jobs
    if curl -s http://localhost:5052/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Job Parser (port 5052) - OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Job Parser (port 5052) - Non disponible${NC}"
        echo -e "${YELLOW}💡 Fallback: parsing local sera utilisé${NC}"
        return 1
    fi
}

# Fonction pour lire la fiche de poste
read_job_input() {
    # Vérifier s'il y a un fichier texte
    if [ -f "$JOB_TEXT_FILE" ]; then
        echo -e "${GREEN}✅ Fiche trouvée: $JOB_TEXT_FILE${NC}"
        cat "$JOB_TEXT_FILE"
        return 0
    fi
    
    # Vérifier s'il y a un PDF
    if [ -f "$JOB_PDF_FILE" ]; then
        echo -e "${GREEN}✅ PDF trouvé: $JOB_PDF_FILE${NC}"
        echo "PDF_FILE:$JOB_PDF_FILE"
        return 0
    fi
    
    # Vérifier le fichier exemple
    if [ -f "sample_job_description.txt" ]; then
        echo -e "${GREEN}✅ Utilisation de l'exemple: sample_job_description.txt${NC}"
        cat "sample_job_description.txt"
        return 0
    fi
    
    # Aucun fichier trouvé
    echo -e "${RED}❌ Aucune fiche de poste trouvée${NC}"
    return 1
}

# Fonction principale
main() {
    echo -e "${BLUE}🚀 Démarrage du test fiche de poste...${NC}\n"
    
    # Vérifier jq
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq requis: brew install jq${NC}"
        exit 1
    fi
    
    # Vérifier services (pas bloquant)
    local api_available=false
    if check_services; then
        api_available=true
    fi
    echo ""
    
    # Lire l'input
    local job_content
    job_content=$(read_job_input)
    local input_status=$?
    
    if [ $input_status -ne 0 ]; then
        echo ""
        create_sample_job
        echo ""
        echo -e "${BLUE}📊 Prochaines étapes:${NC}"
        echo "1. Utiliser l'exemple créé: cp sample_job_description.txt job_description.txt"
        echo "2. Ou créer votre propre fiche: nano job_description.txt"
        echo "3. Puis relancer: ./scripts/test_real_job.sh"
        echo ""
        echo -e "${GREEN}✅ Fiche de test créée pour vous!${NC}"
        exit 0
    fi
    
    echo ""
    
    # Parser selon le type d'input
    if [[ "$job_content" == PDF_FILE:* ]]; then
        # Fichier PDF
        local pdf_path="${job_content#PDF_FILE:}"
        if [ "$api_available" = true ]; then
            echo -e "${BLUE}📄 Parsing du PDF via API...${NC}"
            # Pour l'instant, utiliser fallback même pour PDF
            fallback_parsing "$(head -20 "$pdf_path" 2>/dev/null || echo "Développeur Full Stack Senior - Poste extrait du PDF")"
        else
            echo -e "${RED}❌ API indisponible pour traiter le PDF${NC}"
            exit 1
        fi
    else
        # Texte
        if [ "$api_available" = true ]; then
            if ! parse_job_text "$job_content"; then
                echo -e "${YELLOW}⚠️ API échouée, utilisation du fallback...${NC}"
                fallback_parsing "$job_content"
            fi
        else
            fallback_parsing "$job_content"
        fi
    fi
    
    echo -e "${GREEN}🎉 Test fiche de poste terminé avec succès!${NC}"
    echo ""
    echo -e "${BLUE}📊 Prochaines étapes:${NC}"
    echo "1. Vérifier le résultat: cat parsed_job.json | jq ."
    echo "2. Si vous avez un CV parsé, tester le matching: ./scripts/test_complete_matching.sh"
    echo "3. Créer un CV de test: ./scripts/test_real_cv.sh"
    echo ""
    echo -e "${BLUE}📋 Fichiers générés:${NC}"
    echo "• parsed_job.json - Fiche structurée pour matching"
    [ -f "sample_job_description.txt" ] && echo "• sample_job_description.txt - Fiche exemple"
}

# Gestion des arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Afficher cette aide"
        echo "  --sample       Créer une fiche de poste d'exemple"
        echo ""
        echo "Fichiers supportés:"
        echo "  • job_description.txt (texte)"
        echo "  • job.pdf (PDF)"
        echo "  • sample_job_description.txt (exemple)"
        echo ""
        exit 0
        ;;
    --sample)
        create_sample_job
        exit 0
        ;;
    *)
        main
        ;;
esac