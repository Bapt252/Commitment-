#!/bin/bash
echo "🔄 Synchronisation Git SuperSmartMatch V2..."

# Sauvegarder les changements locaux
git stash push -m "Sauvegarde avant sync"

# Récupérer les changements du remote
git pull origin main

# Restaurer et commiter
git stash pop || echo "Pas de stash"
git add -A
git commit -m "🚀 SuperSmartMatch V2 - Synchronisation finale

✅ Services V2 opérationnels et testés:
- CV Parser V2 (port 5051) - extraction missions
- Job Parser V2 (port 5053) - catégorisation enrichie
- Scoring 40% missions fonctionnel
- APIs REST prêtes pour intégration"

git push origin main
echo "✅ Synchronisation terminée!"
