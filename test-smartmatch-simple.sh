#!/bin/bash
# Script pour tester Nexten SmartMatch sans dépendances complexes
# Auteur: Claude/Anthropic
# Date: 14/05/2025

# Couleurs pour le terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Test de Nexten SmartMatch ===${NC}"
echo "Ce script crée un environnement minimal pour tester le système de matching bidirectionnel."

# Vérifier si la clé API Google Maps est définie
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    echo -e "${YELLOW}Aucune clé API Google Maps n'est définie. Utilisation de la clé par défaut.${NC}"
    export GOOGLE_MAPS_API_KEY="AIzaSyC5cpNgAXN1U0L14pB4HmD7BvP8pD6K8t8"
fi

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Créer un répertoire temporaire pour le test
TEST_DIR="smartmatch_test"
mkdir -p $TEST_DIR

echo -e "${BLUE}Création des fichiers nécessaires...${NC}"

# Créer un fichier Python minimaliste pour le test
cat > $TEST_DIR/smartmatch_test.py << 'EOF'
"""
Test simplifié de Nexten SmartMatch
"""

import os
import json
import time

class SimpleSmartMatcher:
    """
    Version simplifiée du SmartMatcher pour les tests
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")
        print(f"Initialisation avec la clé API: {self.api_key[:5]}...")
    
    def calculate_match(self, candidate, job):
        """
        Calcule un score de matching simple
        """
        # Simuler le traitement
        print(f"Matching du candidat {candidate['name']} avec l'offre {job['title']}...")
        
        # Calculer le score de compétences
        candidate_skills = set(s.lower() for s in candidate.get("skills", []))
        required_skills = set(s.lower() for s in job.get("required_skills", []))
        preferred_skills = set(s.lower() for s in job.get("preferred_skills", []))
        
        # Compter les compétences correspondantes
        required_matches = len(candidate_skills.intersection(required_skills))
        preferred_matches = len(candidate_skills.intersection(preferred_skills))
        
        # Calculer les scores
        required_score = required_matches / len(required_skills) if required_skills else 0.5
        preferred_score = preferred_matches / len(preferred_skills) if preferred_skills else 0.5
        
        # Score final
        overall_score = (required_score * 0.7) + (preferred_score * 0.3)
        
        return {
            "candidate_id": candidate.get("id", ""),
            "job_id": job.get("id", ""),
            "candidate_name": candidate.get("name", ""),
            "job_title": job.get("title", ""),
            "overall_score": round(overall_score, 2),
            "skills_match": {
                "required": required_matches,
                "required_total": len(required_skills),
                "preferred": preferred_matches,
                "preferred_total": len(preferred_skills)
            }
        }
    
    def load_test_data(self):
        """
        Charge des données de test pour le matching
        """
        # Données candidates de test
        candidates = [
            {
                "id": "c1",
                "name": "Jean Dupont",
                "skills": ["Python", "Django", "JavaScript", "React", "SQL", "Git"],
                "location": "48.8566,2.3522",  # Paris
                "years_of_experience": 5
            },
            {
                "id": "c2",
                "name": "Marie Martin",
                "skills": ["Java", "Spring", "Hibernate", "PostgreSQL", "Docker", "Kubernetes"],
                "location": "45.7640,4.8357",  # Lyon
                "years_of_experience": 8
            }
        ]
        
        # Données d'offres d'emploi de test
        jobs = [
            {
                "id": "j1",
                "title": "Développeur Python Senior",
                "required_skills": ["Python", "Django", "SQL"],
                "preferred_skills": ["React", "Docker", "AWS"],
                "location": "48.8847,2.2967",  # Levallois-Perret
                "min_years_of_experience": 4
            },
            {
                "id": "j2",
                "title": "Architecte Java",
                "required_skills": ["Java", "Spring", "Microservices"],
                "preferred_skills": ["AWS", "CI/CD", "Terraform"],
                "location": "48.8566,2.3522",  # Paris
                "min_years_of_experience": 5
            }
        ]
        
        return {"candidates": candidates, "jobs": jobs}

def run_test():
    """
    Exécute un test simple du matching
    """
    print("Démarrage du test SmartMatch...")
    
    # Initialiser le matcher
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    matcher = SimpleSmartMatcher(api_key=api_key)
    
    # Charger les données de test
    data = matcher.load_test_data()
    candidates = data["candidates"]
    jobs = data["jobs"]
    
    print(f"\nDonnées chargées: {len(candidates)} candidats, {len(jobs)} offres d'emploi")
    
    # Exécuter le matching
    results = []
    
    for candidate in candidates:
        for job in jobs:
            start_time = time.time()
            match_result = matcher.calculate_match(candidate, job)
            duration = time.time() - start_time
            
            results.append(match_result)
            
            print(f"Match: {match_result['candidate_name']} -> {match_result['job_title']}")
            print(f"  Score: {match_result['overall_score']:.2f}")
            print(f"  Compétences requises: {match_result['skills_match']['required']}/{match_result['skills_match']['required_total']}")
            print(f"  Compétences préférées: {match_result['skills_match']['preferred']}/{match_result['skills_match']['preferred_total']}")
            print(f"  Durée: {duration:.4f}s\n")
    
    # Afficher le meilleur match
    best_match = max(results, key=lambda x: x['overall_score'])
    print(f"Meilleur match: {best_match['candidate_name']} -> {best_match['job_title']} (Score: {best_match['overall_score']:.2f})")
    
    print("\nTest terminé avec succès!")

if __name__ == "__main__":
    run_test()
EOF

# Rendre le script exécutable
chmod +x $TEST_DIR/smartmatch_test.py

echo -e "${GREEN}Fichiers créés avec succès dans le répertoire $TEST_DIR${NC}"
echo -e "${BLUE}Exécution du test...${NC}"

# Exécuter le test
cd $TEST_DIR
python3 smartmatch_test.py

# Nettoyer
echo -e "\n${BLUE}Nettoyage...${NC}"
cd ..
read -p "Voulez-vous supprimer le répertoire de test? (o/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    rm -rf $TEST_DIR
    echo -e "${GREEN}Répertoire de test supprimé.${NC}"
else
    echo -e "${YELLOW}Le répertoire de test a été conservé: $TEST_DIR${NC}"
fi

echo -e "${GREEN}Test terminé!${NC}"
echo -e "${BLUE}Pour explorer le système SmartMatch complet, vous pouvez consulter le code dans:${NC}"
echo -e "  - matching-service/app/smartmatch.py"
echo -e "  - matching-service/test_smartmatch.py"
echo -e "  - matching-service/test_smartmatch_unit.py"
echo -e "  - matching-service/README-SMARTMATCH.md"
