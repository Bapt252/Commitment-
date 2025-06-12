#!/bin/bash
# Script pour rendre les scripts Session 8 exécutables

echo "Rendre les scripts Session 8 exécutables..."

# Rendre le fichier d'adaptation exécutable
chmod +x fix_session8_imports.sh
echo "✅ fix_session8_imports.sh est maintenant exécutable"

# Rendre le script de test exécutable
chmod +x test_session8.sh
echo "✅ test_session8.sh est maintenant exécutable"

# Rendre le script de démonstration exécutable
chmod +x demo_session8.sh
echo "✅ demo_session8.sh est maintenant exécutable"

# Créer le répertoire scripts s'il n'existe pas
mkdir -p scripts

# Rendre les scripts utilitaires exécutables
chmod +x scripts/start_profile_api.sh 2>/dev/null || true
chmod +x scripts/stop_profile_api.sh 2>/dev/null || true
chmod +x scripts/setup_session8.sh 2>/dev/null || true

echo "Tous les scripts sont maintenant exécutables!"
echo ""
echo "Vous pouvez exécuter les commandes suivantes:"
echo "  ./fix_session8_imports.sh   - Corriger les importations et configurer le port"
echo "  ./test_session8.sh          - Tester l'installation de Session 8"
echo "  ./demo_session8.sh          - Exécuter une démonstration des fonctionnalités"
