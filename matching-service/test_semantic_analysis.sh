#!/bin/bash
# Script pour tester l'analyse sémantique des compétences

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Pas de couleur

echo -e "${BLUE}=== TEST DE L'ANALYSE SÉMANTIQUE DES COMPÉTENCES ===${NC}"

# Vérifier si le script d'installation a été exécuté
if [ ! -f "install_semantic_analysis.sh" ]; then
    echo -e "${YELLOW}⚠️ Le script d'installation 'install_semantic_analysis.sh' n'est pas disponible.${NC}"
    echo -e "${YELLOW}⚠️ Les dépendances nécessaires peuvent ne pas être installées.${NC}"
else
    # Vérifier si le script d'installation a été exécuté
    if [ ! -f "test_semantic_analysis.py" ]; then
        echo -e "${YELLOW}⚠️ Le script de test 'test_semantic_analysis.py' n'est pas disponible.${NC}"
        echo -e "${YELLOW}⚠️ Exécution du script d'installation pour le créer...${NC}"
        chmod +x install_semantic_analysis.sh
        ./install_semantic_analysis.sh
    fi
fi

# Vérifier les dépendances
DEPS_OK=true

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 n'est pas installé${NC}"
    DEPS_OK=false
else
    echo -e "${GREEN}✅ Python3 est installé${NC}"
fi

# Vérifier sentence-transformers
python3 -c "import sentence_transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Le module 'sentence-transformers' n'est pas installé.${NC}"
    echo -e "${YELLOW}⚠️ L'analyse sémantique avancée sera désactivée.${NC}"
    echo -e "${YELLOW}⚠️ Installer avec: pip install sentence-transformers${NC}"
else
    echo -e "${GREEN}✅ Le module 'sentence-transformers' est installé${NC}"
fi

# Vérifier nltk
python3 -c "import nltk" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Le module 'nltk' n'est pas installé${NC}"
    echo -e "${YELLOW}⚠️ Installer avec: pip install nltk${NC}"
    DEPS_OK=false
else
    echo -e "${GREEN}✅ Le module 'nltk' est installé${NC}"
fi

# Vérifier scikit-learn
python3 -c "import sklearn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Le module 'scikit-learn' n'est pas installé${NC}"
    echo -e "${YELLOW}⚠️ Installer avec: pip install scikit-learn${NC}"
    DEPS_OK=false
else
    echo -e "${GREEN}✅ Le module 'scikit-learn' est installé${NC}"
fi

# Vérifier pandas et matplotlib pour les tests avancés
python3 -c "import pandas, matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Les modules 'pandas' et 'matplotlib' ne sont pas installés${NC}"
    echo -e "${YELLOW}⚠️ Les tests avancés ne seront pas disponibles${NC}"
    ADVANCED_TESTS=false
else
    echo -e "${GREEN}✅ Les modules pour les tests avancés sont installés${NC}"
    ADVANCED_TESTS=true
fi

# Si des dépendances sont manquantes, proposer l'installation
if [ "$DEPS_OK" = false ]; then
    echo -e "${YELLOW}Des dépendances sont manquantes. Voulez-vous les installer maintenant ? (y/n)${NC}"
    read INSTALL
    if [[ $INSTALL == "y" || $INSTALL == "Y" ]]; then
        echo -e "${BLUE}Installation des dépendances...${NC}"
        pip install nltk scikit-learn
        python3 -c "import nltk; nltk.download('wordnet'); nltk.download('punkt'); nltk.download('stopwords')"
    else
        echo -e "${YELLOW}⚠️ Les tests peuvent échouer en raison de dépendances manquantes${NC}"
    fi
fi

# Vérifier l'existence des fichiers nécessaires
REQUIRED_FILES=("app/semantic_skills_analyzer.py" "app/skills_taxonomy.py" "app/smartmatch_semantic_enhanced.py")
FILES_OK=true

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Fichier manquant: $file${NC}"
        FILES_OK=false
    else
        echo -e "${GREEN}✅ Fichier trouvé: $file${NC}"
    fi
done

if [ "$FILES_OK" = false ]; then
    echo -e "${RED}❌ Des fichiers nécessaires sont manquants. Les tests peuvent échouer.${NC}"
fi

# Créer le répertoire des résultats
RESULTS_DIR="semantic_test_results"
mkdir -p $RESULTS_DIR

echo -e "${BLUE}=== EXÉCUTION DES TESTS DE BASE ===${NC}"

# Test de base de l'analyseur sémantique
if [ -f "test_semantic_analysis.py" ]; then
    echo -e "${BLUE}Test de l'analyseur sémantique...${NC}"
    python3 test_semantic_analysis.py > $RESULTS_DIR/basic_test.log
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Test de base réussi${NC}"
        echo -e "${YELLOW}⚠️ Consultez le fichier $RESULTS_DIR/basic_test.log pour les détails${NC}"
    else
        echo -e "${RED}❌ Le test de base a échoué${NC}"
        echo -e "${YELLOW}⚠️ Consultez le fichier $RESULTS_DIR/basic_test.log pour les détails${NC}"
    fi
else
    echo -e "${RED}❌ Fichier test_semantic_analysis.py non trouvé${NC}"
fi

# Test de comparaison des algorithmes
if [ "$ADVANCED_TESTS" = true ] && [ -f "test_semantic_comparison.py" ]; then
    echo -e "${BLUE}=== EXÉCUTION DES TESTS AVANCÉS ===${NC}"
    echo -e "${BLUE}Comparaison des algorithmes de matching...${NC}"
    
    python3 test_semantic_comparison.py --output $RESULTS_DIR > $RESULTS_DIR/comparison_test.log
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Test de comparaison réussi${NC}"
        echo -e "${YELLOW}⚠️ Consultez le fichier $RESULTS_DIR/comparison_test.log pour les détails${NC}"
        echo -e "${YELLOW}⚠️ Les graphiques ont été enregistrés dans le répertoire $RESULTS_DIR${NC}"
    else
        echo -e "${RED}❌ Le test de comparaison a échoué${NC}"
        echo -e "${YELLOW}⚠️ Consultez le fichier $RESULTS_DIR/comparison_test.log pour les détails${NC}"
    fi
elif [ -f "test_semantic_comparison.py" ]; then
    echo -e "${YELLOW}⚠️ Tests avancés non disponibles - modules pandas et matplotlib manquants${NC}"
else
    echo -e "${YELLOW}⚠️ Fichier test_semantic_comparison.py non trouvé${NC}"
fi

# Test d'intégration avec le SmartMatcher
echo -e "${BLUE}=== TEST D'INTÉGRATION AVEC SMARTMATCHER ===${NC}"

# Créer un script de test d'intégration simple
cat > test_semantic_integration.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'intégration de l'analyse sémantique avec SmartMatcher
"""

import logging
import sys
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Importer le SmartMatcher amélioré
    from app.smartmatch_semantic_enhanced import get_semantic_enhanced_matcher
    
    # Créer une instance avec mode de secours pour éviter les dépendances manquantes
    logger.info("Initialisation du SmartMatcher avec analyse sémantique...")
    matcher = get_semantic_enhanced_matcher()
    
    # Données de test simples
    candidate = {
        "id": "test_candidate",
        "name": "Test Candidate",
        "skills": ["Python3", "JavaScript", "ReactJS", "ML", "CI/CD"],
        "location": "Paris, France",
        "years_of_experience": 5,
        "education_level": "master"
    }
    
    job = {
        "id": "test_job",
        "title": "Full Stack Developer",
        "required_skills": ["Python", "React", "JavaScript"],
        "preferred_skills": ["Machine Learning", "DevOps"],
        "location": "Paris, France",
        "min_years_of_experience": 3,
        "required_education": "bachelor"
    }
    
    # Calculer le matching
    logger.info("Calcul du matching...")
    result = matcher.calculate_match(candidate, job)
    
    # Afficher les résultats
    print("\n=== RÉSULTATS DU MATCHING ===")
    print(f"Score global: {result['overall_score']:.4f}")
    print(f"Score de compétences: {result['category_scores']['skills']:.4f}")
    
    print("\n=== INSIGHTS ===")
    for insight in result["insights"]:
        print(f"- {insight['message']} ({insight['category']})")
    
    print("\nTest d'intégration réussi!")
    sys.exit(0)
    
except Exception as e:
    logger.error(f"Erreur lors du test d'intégration: {str(e)}")
    sys.exit(1)
EOF

# Rendre le script exécutable
chmod +x test_semantic_integration.py

# Exécuter le test d'intégration
python3 test_semantic_integration.py > $RESULTS_DIR/integration_test.log

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test d'intégration réussi${NC}"
    echo -e "${YELLOW}⚠️ Consultez le fichier $RESULTS_DIR/integration_test.log pour les détails${NC}"
else
    echo -e "${RED}❌ Le test d'intégration a échoué${NC}"
    echo -e "${YELLOW}⚠️ Consultez le fichier $RESULTS_DIR/integration_test.log pour les détails${NC}"
fi

# Résumé
echo -e "${BLUE}=== RÉSUMÉ DES TESTS ===${NC}"
echo -e "${GREEN}Tous les tests ont été exécutés${NC}"
echo -e "${YELLOW}Les résultats détaillés sont disponibles dans le répertoire: $RESULTS_DIR${NC}"
echo -e "${BLUE}=== DOCUMENTATION ===${NC}"
echo -e "${YELLOW}Pour plus d'informations, consultez:${NC}"
echo -e "  - README-SEMANTIC-ANALYSIS.md - Documentation principale"
echo -e "  - README-SKILLS-ENHANCEMENT.md - Explications sur les améliorations"

# Nettoyage
echo -e "${BLUE}=== NETTOYAGE ===${NC}"
echo -e "${YELLOW}Les fichiers temporaires de test ont été conservés pour référence.${NC}"
echo -e "${YELLOW}Voulez-vous les supprimer ? (y/n)${NC}"
read CLEAN

if [[ $CLEAN == "y" || $CLEAN == "Y" ]]; then
    rm test_semantic_integration.py
    echo -e "${GREEN}✅ Fichiers temporaires supprimés${NC}"
else
    echo -e "${YELLOW}⚠️ Fichiers temporaires conservés${NC}"
fi

echo -e "${BLUE}=== TESTS TERMINÉS ===${NC}"
