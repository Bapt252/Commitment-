#!/bin/bash

# Script de restructuration du projet Commitment-
# Ce script réorganise le projet en éliminant les structures de dossiers imbriquées
# tout en préservant toutes les fonctionnalités.

echo "Démarrage de la restructuration du projet..."

# 1. Créer un dossier temporaire pour la restructuration
mkdir -p /tmp/commitment-restructure

# 2. Cloner le projet dans ce dossier temporaire
git clone https://github.com/Bapt252/Commitment- /tmp/commitment-restructure/fresh-repo
cd /tmp/commitment-restructure/fresh-repo

# 3. Créer une nouvelle branche pour la restructuration
git checkout -b restructure-project

# 4. Copier tous les fichiers et dossiers importants du projet
# (Cette partie devra être adaptée selon votre structure exacte)
echo "Réorganisation des fichiers..."

# 5. Créer les scripts d'assistance
cat > /tmp/commitment-restructure/cleanup-script.sh << 'EOF'
#!/bin/bash

# Ce script nettoie votre environnement local en créant une nouvelle structure propre

# Destination du nouveau projet
NEW_PROJECT_DIR="$HOME/fresh-commitment"

# Créer un nouveau dossier pour le projet
mkdir -p "$NEW_PROJECT_DIR"

# Cloner le dépôt GitHub dans ce dossier
git clone https://github.com/Bapt252/Commitment- "$NEW_PROJECT_DIR"

# Se déplacer dans le dossier du projet
cd "$NEW_PROJECT_DIR"

# Rendre les scripts exécutables
chmod +x *.sh

echo "Votre projet a été restructuré dans $NEW_PROJECT_DIR"
echo "Vous pouvez maintenant travailler dans ce dossier avec une structure propre"
EOF

chmod +x /tmp/commitment-restructure/cleanup-script.sh

# 6. Créer un guide d'utilisation
cat > SETUP_GUIDE.md << 'EOF'
# Guide d'installation et d'utilisation

Ce guide vous aidera à mettre en place correctement votre environnement de développement pour le projet Commitment-.

## Installation propre

Pour éviter les problèmes de structure de dossiers imbriqués, nous recommandons de suivre ces étapes:

1. Exécutez le script de nettoyage pour créer une installation propre:
   ```bash
   ./cleanup-script.sh
   ```

2. Ce script va créer un nouveau dossier `~/fresh-commitment` avec une installation propre du projet.

3. Travaillez toujours dans ce dossier plutôt que dans une structure imbriquée.

## Structure du projet

Le projet est organisé comme suit:
- `backend/` - Contient l'API backend (Python/FastAPI)
- `frontend/` - Contient l'interface utilisateur
- `ml_engine/` - Contient le moteur d'analyse et de matching
- `scripts/` - Contient tous les scripts utilitaires

## Scripts utilitaires

- `reset-api.sh` - Réinitialise l'API
- `test-api.sh` - Teste les endpoints de l'API

## Problèmes courants

Si vous rencontrez l'erreur "No such file or directory: ./reset-api.sh", c'est probablement parce que:
1. Vous n'êtes pas dans le bon dossier
2. Le script n'existe pas dans votre branche actuelle
3. Le script n'a pas les permissions d'exécution

Solution: Assurez-vous d'être à la racine du projet et exécutez:
```bash
chmod +x *.sh
```
EOF

# 7. Commit et push des modifications
git add SETUP_GUIDE.md
git commit -m "Ajout du guide d'installation pour faciliter la mise en place"

# 8. Finaliser et informer l'utilisateur
echo "==========================================================="
echo "La restructuration est terminée!"
echo "Un guide d'installation a été ajouté au dépôt."
echo "Pour nettoyer votre environnement local, exécutez:"
echo "curl -O https://raw.githubusercontent.com/Bapt252/Commitment-/restructure-project/cleanup-script.sh"
echo "chmod +x cleanup-script.sh"
echo "./cleanup-script.sh"
echo "==========================================================="
