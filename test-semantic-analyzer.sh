#!/usr/bin/env bash
# Script pour exécuter les tests de l'analyseur sémantique

# Vérifier les dépendances
check_dependencies() {
    echo "Vérification des dépendances pour les tests de l'analyseur sémantique..."
    
    # Liste des packages requis
    dependencies=("nltk" "difflib")
    optional_dependencies=("scikit-learn" "tensorflow")
    
    # Vérifier les dépendances requises
    for dep in "${dependencies[@]}"; do
        if python -c "import $dep" &>/dev/null; then
            echo "✓ $dep est installé"
        else
            echo "✗ $dep n'est pas installé. Installation..."
            pip install $dep
        fi
    done
    
    # Vérifier les dépendances optionnelles
    for dep in "${optional_dependencies[@]}"; do
        if python -c "import $dep" &>/dev/null; then
            echo "✓ $dep est installé (optionnel)"
        else
            echo "⚠ $dep n'est pas installé (optionnel). Certaines fonctionnalités peuvent être limitées."
        fi
    done
    
    echo "Vérification des dépendances terminée."
}

# Exécuter les tests
run_tests() {
    echo "Exécution des tests de l'analyseur sémantique..."
    python semantic_analyzer_test.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Tous les tests ont réussi!"
    else
        echo "✗ Certains tests ont échoué. Veuillez consulter les messages d'erreur ci-dessus."
    fi
}

# Intégrer avec le système SmartMatch
integrate_with_smartmatch() {
    echo "Intégration de l'analyseur sémantique avec SmartMatch..."
    
    # Vérifier que le module compat existe
    if [ -d "app/compat" ]; then
        echo "✓ Module compat trouvé"
    else
        echo "✗ Module compat non trouvé. Création..."
        mkdir -p app/compat
        touch app/compat/__init__.py
    fi
    
    # Vérifier que le fichier principal existe
    if [ -f "matching_engine_enhanced.py" ]; then
        echo "✓ Module matching_engine_enhanced.py trouvé"
        
        # Vérifier si l'analyseur sémantique est déjà importé
        if grep -q "SemanticAnalyzer" matching_engine_enhanced.py; then
            echo "✓ Analyseur sémantique déjà intégré"
        else
            echo "⚠ L'analyseur sémantique n'est pas encore intégré dans matching_engine_enhanced.py"
            echo "  Vous devrez modifier ce fichier pour utiliser l'analyseur sémantique."
            echo "  Exemple d'intégration:"
            echo "    from app.semantic.analyzer import SemanticAnalyzer"
            echo "    # Dans la classe EnhancedMatchingEngine:"
            echo "    def __init__(self):"
            echo "        self.semantic_analyzer = SemanticAnalyzer()"
            echo "    # Dans la méthode _calculate_skills_score:"
            echo "    semantic_score = self.semantic_analyzer.calculate_skills_similarity(cv_skills, job_skills)"
        fi
    else
        echo "✗ Module matching_engine_enhanced.py non trouvé"
    fi
}

# Menu principal
echo "=== Tests de l'analyseur sémantique de compétences ==="
echo "1. Vérifier les dépendances"
echo "2. Exécuter les tests"
echo "3. Intégrer avec SmartMatch"
echo "4. Tout exécuter"
echo "5. Quitter"
echo ""
echo "Votre choix: "
read choice

case $choice in
    1)
        check_dependencies
        ;;
    2)
        run_tests
        ;;
    3)
        integrate_with_smartmatch
        ;;
    4)
        check_dependencies
        run_tests
        integrate_with_smartmatch
        ;;
    5)
        echo "Au revoir!"
        exit 0
        ;;
    *)
        echo "Choix invalide. Veuillez réessayer."
        ;;
esac

echo ""
echo "Opération terminée."
