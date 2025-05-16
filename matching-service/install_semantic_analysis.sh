#!/bin/bash
# Script d'installation et de configuration pour l'analyse sémantique des compétences

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Pas de couleur

echo -e "${BLUE}=== INSTALLATION DES DÉPENDANCES POUR L'ANALYSE SÉMANTIQUE DES COMPÉTENCES ===${NC}"

# Vérification de l'environnement virtuel Python
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Environnement virtuel Python détecté${NC}"
    # Activer l'environnement virtuel
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️ Environnement virtuel Python non détecté, création...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel Python créé et activé${NC}"
fi

# Installation des dépendances
echo -e "${BLUE}=== INSTALLATION DES DÉPENDANCES PRINCIPALES ===${NC}"
pip install --upgrade pip
pip install sentence-transformers>=2.2.2 scikit-learn>=1.0.2 nltk>=3.7 pandas>=1.4.0 matplotlib>=3.5.0 tabulate>=0.8.9

# Téléchargement des ressources NLTK
echo -e "${BLUE}=== TÉLÉCHARGEMENT DES RESSOURCES NLTK ===${NC}"
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt'); nltk.download('stopwords')"

# Vérification que les modules sont installés correctement
if python -c "import sentence_transformers" 2>/dev/null; then
    echo -e "${GREEN}✅ Module 'sentence-transformers' installé avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation du module 'sentence-transformers'${NC}"
    echo -e "${YELLOW}⚠️ L'analyse sémantique avancée sera désactivée${NC}"
fi

if python -c "import sklearn" 2>/dev/null; then
    echo -e "${GREEN}✅ Module 'scikit-learn' installé avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation du module 'scikit-learn'${NC}"
    exit 1
fi

if python -c "import nltk" 2>/dev/null; then
    echo -e "${GREEN}✅ Module 'nltk' installé avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation du module 'nltk'${NC}"
    exit 1
fi

# Mise à jour du fichier requirements.txt
echo -e "${BLUE}=== MISE À JOUR DU FICHIER REQUIREMENTS.TXT ===${NC}"

if [ -f "requirements.txt" ]; then
    # Vérifier si les modules sont déjà dans requirements.txt
    if ! grep -q "sentence-transformers" requirements.txt; then
        echo "sentence-transformers>=2.2.2" >> requirements.txt
        echo -e "${GREEN}✅ Module 'sentence-transformers' ajouté à requirements.txt${NC}"
    else
        echo -e "${GREEN}✅ Module 'sentence-transformers' déjà présent dans requirements.txt${NC}"
    fi
    
    if ! grep -q "nltk" requirements.txt; then
        echo "nltk>=3.7" >> requirements.txt
        echo -e "${GREEN}✅ Module 'nltk' ajouté à requirements.txt${NC}"
    else
        echo -e "${GREEN}✅ Module 'nltk' déjà présent dans requirements.txt${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Fichier requirements.txt non trouvé, création...${NC}"
    cat > requirements.txt << EOF
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
sentence-transformers>=2.2.2
scikit-learn>=1.0.2
nltk>=3.7
pandas>=1.4.0
matplotlib>=3.5.0
tabulate>=0.8.9
python-dotenv>=0.21.0
EOF
    echo -e "${GREEN}✅ Fichier requirements.txt créé${NC}"
fi

# Téléchargement et mise en cache des modèles d'embeddings
echo -e "${BLUE}=== TÉLÉCHARGEMENT DES MODÈLES D'EMBEDDINGS ===${NC}"
echo -e "${YELLOW}Ce processus peut prendre plusieurs minutes la première fois...${NC}"

# Création du script Python pour télécharger les modèles
cat > download_models.py << EOF
from sentence_transformers import SentenceTransformer
import os
import sys

# Fonction pour télécharger et mettre en cache un modèle
def download_model(model_name):
    try:
        print(f"Téléchargement du modèle {model_name}...")
        model = SentenceTransformer(model_name)
        print(f"Modèle {model_name} téléchargé et mis en cache avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors du téléchargement du modèle {model_name}: {str(e)}")
        return False

# Liste des modèles à télécharger
models = [
    'paraphrase-multilingual-MiniLM-L12-v2',  # Modèle multilingue léger (par défaut)
    'all-MiniLM-L6-v2'                        # Modèle anglais plus léger
]

# Télécharger chaque modèle
success = True
for model_name in models:
    if not download_model(model_name):
        success = False

sys.exit(0 if success else 1)
EOF

# Exécuter le script de téléchargement
python download_models.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Modèles d'embeddings téléchargés avec succès${NC}"
else
    echo -e "${YELLOW}⚠️ Problèmes lors du téléchargement des modèles d'embeddings${NC}"
    echo -e "${YELLOW}⚠️ L'analyse sémantique pourrait ne pas fonctionner correctement${NC}"
fi

# Suppression du script temporaire
rm download_models.py

# Création du script de test
echo -e "${BLUE}=== CRÉATION DU SCRIPT DE TEST ===${NC}"
cat > test_semantic_analysis.py << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour l'analyse sémantique des compétences
"""

import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_embeddings():
    """Teste la génération d'embeddings et le calcul de similarité"""
    logger.info("Test de génération d'embeddings...")
    
    # Chargement du modèle
    try:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("✅ Modèle chargé avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement du modèle: {str(e)}")
        return False
    
    # Liste de compétences à comparer
    skills = [
        "Python",
        "Python programming",
        "Django",
        "Flask",
        "JavaScript",
        "React",
        "ReactJS",
        "Machine Learning",
        "ML",
        "Deep Learning"
    ]
    
    # Calculer les embeddings
    try:
        embeddings = model.encode(skills)
        logger.info(f"✅ Embeddings générés pour {len(skills)} compétences")
    except Exception as e:
        logger.error(f"❌ Erreur lors du calcul des embeddings: {str(e)}")
        return False
    
    # Calculer les similarités
    similarities = cosine_similarity(embeddings)
    
    # Afficher les résultats
    logger.info("=== Résultats de similarité entre compétences ===")
    for i in range(len(skills)):
        for j in range(i+1, len(skills)):
            sim = similarities[i, j]
            logger.info(f"{skills[i]} <-> {skills[j]}: {sim:.4f}")
    
    return True

if __name__ == "__main__":
    logger.info("=== TEST DE L'ANALYSE SÉMANTIQUE DES COMPÉTENCES ===")
    
    if test_embeddings():
        logger.info("✅ Tous les tests d'embeddings ont réussi")
    else:
        logger.error("❌ Les tests d'embeddings ont échoué")
EOF

chmod +x test_semantic_analysis.py
echo -e "${GREEN}✅ Script de test créé : test_semantic_analysis.py${NC}"

# Instructions finales
echo -e "${BLUE}=== INSTALLATION TERMINÉE ===${NC}"
echo -e "${YELLOW}Pour tester l'analyse sémantique des compétences, exécutez :${NC}"
echo -e "  ./test_semantic_analysis.py"

echo -e "${BLUE}=== INFORMATIONS IMPORTANTES ===${NC}"
echo -e "${YELLOW}Si vous prévoyez de traiter un grand volume de données :${NC}"
echo -e "1. Pensez à installer un serveur Redis pour améliorer les performances du cache"
echo -e "2. Modifiez le paramètre cache_size dans le code pour l'adapter à vos besoins"
echo -e "3. Utilisez le même modèle d'embeddings dans toute votre application pour optimiser l'utilisation de la mémoire"
