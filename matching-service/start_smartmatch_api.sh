#!/bin/bash

# Script de démarrage de l'API SmartMatch
echo "Démarrage de l'API SmartMatch..."

# Vérifier si une clé API Google Maps est définie
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    # Essayer de charger depuis .env
    if [ -f .env ]; then
        source .env
    fi
    
    # Si toujours pas définie, demander à l'utilisateur
    if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
        echo "Aucune clé API Google Maps trouvée."
        read -p "Voulez-vous saisir une clé API Google Maps ? (o/n): " answer
        
        if [[ "$answer" == "o" || "$answer" == "O" || "$answer" == "oui" ]]; then
            read -p "Entrez votre clé API Google Maps: " api_key
            export GOOGLE_MAPS_API_KEY="$api_key"
            
            # Sauvegarder dans .env pour les prochaines utilisations
            echo "GOOGLE_MAPS_API_KEY=\"$api_key\"" >> .env
            echo "Clé API Google Maps sauvegardée dans .env"
        else
            echo "Aucune clé API Google Maps fournie. Certaines fonctionnalités seront limitées."
        fi
    fi
fi

# Démarrer l'API avec Uvicorn
echo "Lancement de l'API sur http://localhost:5052"
python -m uvicorn app.api.smartmatch_api:app --host 0.0.0.0 --port 5052 --reload