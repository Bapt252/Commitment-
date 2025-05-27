#!/bin/bash

# Script de démarrage rapide pour tester l'algorithme de matching
# Usage: ./quick_test.sh

echo "🚀 DÉMARRAGE RAPIDE - TEST ALGORITHME DE MATCHING"
echo "=================================================="

# Vérifier si on est dans le bon répertoire
if [ ! -f "matching_engine.py" ]; then
    echo "❌ Fichier matching_engine.py non trouvé"
    echo "Assurez-vous d'être dans le répertoire Commitment-"
    exit 1
fi

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé"
    echo "Installez Python3 pour continuer"
    exit 1
fi

echo "✅ Environnement vérifié"
echo ""

echo "📋 Options disponibles:"
echo "1. Test direct de l'algorithme (recommandé)"
echo "2. Lancer l'API de test sur le port 8001"
echo "3. Test simple rapide"
echo ""

read -p "Choisissez une option (1-3): " choice

case $choice in
    1)
        echo "🔥 Lancement du test direct..."
        python3 test_algorithm_direct.py
        ;;
    2)
        echo "🌐 Lancement de l'API de test..."
        echo "API disponible sur: http://localhost:8001"
        echo "Documentation: http://localhost:8001/docs"
        echo "Appuyez sur Ctrl+C pour arrêter"
        python3 test_algorithm.py
        ;;
    3)
        echo "⚡ Test simple rapide..."
        python3 -c "
from matching_engine import match_candidate_with_jobs
import json

print('🧪 Test rapide de l\'algorithme...')

cv_data = {
    'competences': ['Python', 'Django', 'React'],
    'annees_experience': 3,
    'formation': 'Master Informatique'
}

questionnaire_data = {
    'contrats_recherches': ['CDI'],
    'adresse': 'Paris',
    'salaire_min': 45000
}

job_data = [{
    'id': 1,
    'titre': 'Développeur Full-Stack',
    'entreprise': 'TechCorp',
    'competences': ['Python', 'Django', 'React'],
    'type_contrat': 'CDI',
    'salaire': '45K-55K€'
}]

results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
print('✅ Résultat:', json.dumps(results[0], indent=2, ensure_ascii=False))
"
        ;;
    *)
        echo "❌ Option non valide"
        exit 1
        ;;
esac

echo ""
echo "🎉 Test terminé !"
echo ""
echo "📚 ÉTAPES SUIVANTES:"
echo "• Analyser les résultats obtenus"
echo "• Modifier matching_engine.py avec votre algorithme"  
echo "• Relancer les tests pour comparer"
echo "• Intégrer dans le système complet"
