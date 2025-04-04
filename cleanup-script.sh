#!/bin/bash

# Script de nettoyage pour corriger les structures imbriquées du projet Commitment-
# Ce script crée une installation propre du projet dans un nouveau dossier

echo "=== Démarrage du nettoyage du projet Commitment- ==="

# Destination du nouveau projet
NEW_PROJECT_DIR="$HOME/fresh-commitment"

# Demander confirmation
echo "Ce script va créer un nouveau dossier: $NEW_PROJECT_DIR"
echo "Voulez-vous continuer? (o/n)"
read -r answer
if [[ "$answer" != "o" && "$answer" != "O" ]]; then
    echo "Opération annulée."
    exit 0
fi

# Vérifier si le dossier existe déjà
if [ -d "$NEW_PROJECT_DIR" ]; then
    echo "Le dossier $NEW_PROJECT_DIR existe déjà."
    echo "Voulez-vous le supprimer et le recréer? (o/n)"
    read -r answer
    if [[ "$answer" != "o" && "$answer" != "O" ]]; then
        echo "Opération annulée."
        exit 0
    fi
    rm -rf "$NEW_PROJECT_DIR"
fi

# Créer un nouveau dossier pour le projet
mkdir -p "$NEW_PROJECT_DIR"
echo "Dossier créé: $NEW_PROJECT_DIR"

# Cloner le dépôt GitHub dans ce dossier
echo "Clonage du dépôt dans le nouveau dossier..."
git clone https://github.com/Bapt252/Commitment- "$NEW_PROJECT_DIR"

# Se déplacer dans le dossier du projet
cd "$NEW_PROJECT_DIR" || { echo "Impossible d'accéder au dossier $NEW_PROJECT_DIR"; exit 1; }

# Vérifier la branche actuelle et informer l'utilisateur
current_branch=$(git branch --show-current)
echo "Vous êtes maintenant sur la branche: $current_branch"

# Liste des branches disponibles
echo "Branches disponibles:"
git branch -r | grep -v '\->' | sed "s/origin\///"

# Demander quelle branche utiliser
echo "Voulez-vous passer à une autre branche? (Entrez le nom de la branche ou laissez vide pour conserver $current_branch)"
read -r branch_name

if [ -n "$branch_name" ]; then
    echo "Passage à la branche $branch_name..."
    git checkout "$branch_name" || { echo "Impossible de passer à la branche $branch_name"; }
fi

# Rendre les scripts exécutables
echo "Ajout des permissions d'exécution aux scripts..."
find . -name "*.sh" -exec chmod +x {} \;

# Copier le fichier reset-api.sh s'il n'existe pas
if [ ! -f "reset-api.sh" ]; then
    echo "Le fichier reset-api.sh n'existe pas dans cette branche, tentative de récupération..."
    git checkout main -- reset-api.sh 2>/dev/null || \
    curl -s -o reset-api.sh https://raw.githubusercontent.com/Bapt252/Commitment-/main/reset-api.sh
    
    if [ -f "reset-api.sh" ]; then
        chmod +x reset-api.sh
        echo "Fichier reset-api.sh récupéré et rendu exécutable."
    else
        echo "Impossible de récupérer reset-api.sh."
    fi
fi

echo ""
echo "=== Configuration terminée ==="
echo "Votre projet a été restructuré dans $NEW_PROJECT_DIR"
echo "Vous pouvez maintenant travailler dans ce dossier avec une structure propre"

if [ "$current_branch" != "main" ]; then
    echo ""
    echo "REMARQUE: Vous travaillez sur la branche $current_branch qui peut ne pas contenir"
    echo "tous les fichiers présents dans la branche principale (main)."
fi

echo ""
echo "Pour démarrer le travail, exécutez:"
echo "cd $NEW_PROJECT_DIR"
