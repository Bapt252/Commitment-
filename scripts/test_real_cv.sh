#!/bin/bash

echo "🧪 SuperSmartMatch V2 - Test CV Réel"
echo "===================================="

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
CV_PATH="./cv.pdf"
DEFAULT_CV_PATH="./test_cv.pdf"

# Fonction pour vérifier les prérequis
check_prerequisites() {
    echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"
    
    # Vérifier jq
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq n'est pas installé. Installation required: brew install jq${NC}"
        exit 1
    fi
    
    # Vérifier curl
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ curl n'est pas installé${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prérequis OK${NC}"
}

# Fonction pour vérifier les services
check_services() {
    echo -e "${BLUE}🏥 Vérification des services...${NC}"
    
    # Vérifier CV Parser (port 5051)
    if curl -s http://localhost:5051/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ CV Parser (port 5051) - OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ CV Parser (port 5051) - Non disponible${NC}"
        echo -e "${YELLOW}💡 Fallback: génération CV de test simulé${NC}"
        return 1
    fi
}

# Fonction pour trouver un CV de test
find_cv_file() {
    if [ -f "$CV_PATH" ]; then
        echo -e "${GREEN}✅ CV trouvé: $CV_PATH${NC}"
        return 0
    elif [ -f "$DEFAULT_CV_PATH" ]; then
        CV_PATH="$DEFAULT_CV_PATH"
        echo -e "${GREEN}✅ CV trouvé: $CV_PATH${NC}"
        return 0
    else
        echo -e "${RED}❌ Aucun CV trouvé${NC}"
        echo -e "${YELLOW}📝 Placez votre CV en PDF dans le dossier courant:${NC}"
        echo "   • cv.pdf"
        echo "   • test_cv.pdf"
        return 1
    fi
}

# Fonction pour parser le CV
parse_cv() {
    echo -e "${BLUE}📤 Parsing du CV: $CV_PATH${NC}"
    
    # Upload du CV à l'API de parsing
    echo "   🔄 Upload en cours..."
    RESPONSE=$(curl -s -X POST http://localhost:5051/api/queue \
        -F "file=@$CV_PATH" \
        -F "priority=premium" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur lors de l'upload du CV${NC}"
        return 1
    fi
    
    # Extraire l'ID du job
    JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id' 2>/dev/null)
    
    if [ "$JOB_ID" == "null" ] || [ -z "$JOB_ID" ]; then
        echo -e "${RED}❌ Erreur parsing. Réponse serveur:${NC}"
        echo "$RESPONSE"
        return 1
    fi
    
    echo -e "${GREEN}✅ Job créé avec ID: $JOB_ID${NC}"
    
    # Attendre le résultat du parsing
    echo "   ⏳ Traitement en cours..."
    for i in {1..20}; do
        echo "      ⌛ Tentative $i/20..."
        RESULT=$(curl -s http://localhost:5051/api/result/$JOB_ID 2>/dev/null)
        STATUS=$(echo "$RESULT" | jq -r '.status' 2>/dev/null)
        
        if [[ "$STATUS" == "completed" ]]; then
            echo -e "${GREEN}✅ CV parsé avec succès!${NC}"
            
            # Sauvegarder le résultat
            echo "$RESULT" | jq . > parsed_cv.json 2>/dev/null
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}💾 CV structuré sauvegardé: parsed_cv.json${NC}"
                
                # Afficher un aperçu
                CANDIDATE_NAME=$(echo "$RESULT" | jq -r '.data.personal_info.name // "Nom non détecté"' 2>/dev/null)
                SKILLS_COUNT=$(echo "$RESULT" | jq -r '.data.skills | length // 0' 2>/dev/null)
                EXPERIENCE=$(echo "$RESULT" | jq -r '.data.extracted_metrics.experience_years // "Non détecté"' 2>/dev/null)
                
                echo ""
                echo -e "${BLUE}📋 Aperçu du CV parsé:${NC}"
                echo "   👤 Candidat: $CANDIDATE_NAME"
                echo "   🛠️ Compétences: $SKILLS_COUNT détectées"
                echo "   📅 Expérience: $EXPERIENCE ans"
                echo ""
                
                return 0
            else
                echo -e "${RED}❌ Erreur lors de la sauvegarde${NC}"
                return 1
            fi
        elif [[ "$STATUS" == "failed" ]]; then
            echo -e "${RED}❌ Parsing échoué${NC}"
            echo "$RESULT" | jq '.error // "Erreur inconnue"'
            return 1
        fi
        
        sleep 2
    done
    
    echo -e "${RED}❌ Timeout: parsing non terminé après 40 secondes${NC}"
    return 1
}

# Fonction pour créer un CV de test si aucun n'existe
create_sample_cv() {
    echo -e "${YELLOW}📝 Création d'un CV de test réaliste...${NC}"
    
    cat > sample_cv.txt << 'EOF'
MARIE DUPONT
Développeuse Full Stack Senior
Email: marie.dupont@email.com
Téléphone: +33 6 12 34 56 78
Adresse: 123 rue de la Paix, 75001 Paris

EXPÉRIENCE PROFESSIONNELLE

Senior Developer - TechCorp (2021-2024)
• Développement d'applications web avec React et Node.js
• Architecture microservices avec Docker et Kubernetes
• Mentorat d'une équipe de 3 développeurs juniors
• Mise en place CI/CD avec GitHub Actions

Full Stack Developer - StartupTech (2019-2021)
• Développement d'une plateforme SaaS avec Python/Django
• Intégration API REST et GraphQL
• Optimisation performance base de données PostgreSQL
• Collaboration en méthode Agile/Scrum

FORMATION
• Master Informatique - École Polytechnique (2019)
• Licence Informatique - Université Paris-Saclay (2017)

COMPÉTENCES TECHNIQUES
• Langages: Python, JavaScript, TypeScript, Java
• Frontend: React, Vue.js, HTML5, CSS3
• Backend: Node.js, Django, Express, FastAPI
• Bases de données: PostgreSQL, MongoDB, Redis
• DevOps: Docker, Kubernetes, AWS, GitHub Actions
• Outils: Git, Jira, Slack, VS Code

LANGUES
• Français (natif)
• Anglais (courant)
• Espagnol (notions)

CERTIFICATIONS
• AWS Solutions Architect Associate
• Scrum Master Certified
EOF

    # Créer aussi un JSON structuré réaliste
    cat > parsed_cv.json << 'EOF'
{
  "status": "success",
  "data": {
    "personal_info": {
      "name": "Marie Dupont",
      "email": "marie.dupont@email.com",
      "phone": "+33 6 12 34 56 78",
      "location": "Paris, France"
    },
    "professional_summary": "Développeuse Full Stack Senior avec 5 ans d'expérience en développement web, spécialisée en React/Node.js et architecture microservices.",
    "skills": [
      "Python", "JavaScript", "TypeScript", "React", "Node.js", "Docker", 
      "Kubernetes", "AWS", "PostgreSQL", "MongoDB", "Redis", "Git", 
      "Django", "Express", "FastAPI", "Vue.js", "HTML5", "CSS3"
    ],
    "experience": [
      {
        "company": "TechCorp",
        "position": "Senior Developer",
        "duration": "2021-2024",
        "location": "Paris",
        "responsibilities": [
          "Développement d'applications web React/Node.js",
          "Architecture microservices Docker/Kubernetes",
          "Mentorat équipe de 3 développeurs juniors",
          "Mise en place CI/CD avec GitHub Actions"
        ]
      },
      {
        "company": "StartupTech", 
        "position": "Full Stack Developer",
        "duration": "2019-2021",
        "location": "Paris",
        "responsibilities": [
          "Développement plateforme SaaS Python/Django",
          "Intégration API REST et GraphQL",
          "Optimisation performance PostgreSQL"
        ]
      }
    ],
    "education": [
      {
        "degree": "Master Informatique",
        "school": "École Polytechnique",
        "year": "2019",
        "location": "Paris"
      },
      {
        "degree": "Licence Informatique",
        "school": "Université Paris-Saclay", 
        "year": "2017",
        "location": "Paris"
      }
    ],
    "languages": ["Français (natif)", "Anglais (courant)", "Espagnol (notions)"],
    "certifications": ["AWS Solutions Architect Associate", "Scrum Master Certified"],
    "extracted_metrics": {
      "experience_years": 5,
      "seniority_level": "senior",
      "industry_experience": ["tech", "startup"],
      "management_experience": true,
      "technical_skills_count": 18,
      "leadership_experience": true
    }
  }
}
EOF

    echo -e "${GREEN}✅ CV de test créé: sample_cv.txt${NC}"
    echo -e "${GREEN}✅ CV parsé simulé créé: parsed_cv.json${NC}"
    
    return 0
}

# Fonction principale
main() {
    echo -e "${BLUE}🚀 Démarrage du test CV réel...${NC}\n"
    
    # Vérifications
    check_prerequisites || exit 1
    echo ""
    
    # Vérifier si l'API de parsing est disponible
    if check_services; then
        echo ""
        
        # Trouver le CV
        if find_cv_file; then
            echo ""
            
            # Parser le CV via API
            if parse_cv; then
                echo -e "${GREEN}🎉 Test CV réel terminé avec succès!${NC}"
            else
                echo -e "${YELLOW}⚠️ Parsing API échoué, création CV de test...${NC}"
                create_sample_cv
            fi
        else
            echo ""
            create_sample_cv
        fi
    else
        echo ""
        echo -e "${YELLOW}💡 API de parsing non disponible, création CV de test...${NC}"
        create_sample_cv
    fi
    
    echo ""
    echo -e "${BLUE}📊 Prochaines étapes:${NC}"
    echo "1. Créer une fiche de poste: ./scripts/test_real_job.sh"
    echo "2. Tester le matching complet: ./scripts/test_complete_matching.sh"
    echo "3. Voir les résultats détaillés: cat parsed_cv.json | jq ."
    echo ""
    echo -e "${BLUE}📈 Dashboards disponibles:${NC}"
    echo "• Grafana: http://localhost:3000"
    echo "• Status Services: docker-compose ps"
}

# Gestion des arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Afficher cette aide"
        echo "  --check        Vérifier seulement les services"
        echo "  --sample       Créer un CV de test"
        echo ""
        echo "Fichiers CV supportés:"
        echo "  • cv.pdf (priorité)"
        echo "  • test_cv.pdf (fallback)"
        echo ""
        exit 0
        ;;
    --check)
        check_prerequisites
        check_services
        exit 0
        ;;
    --sample)
        create_sample_cv
        exit 0
        ;;
    *)
        main
        ;;
esac