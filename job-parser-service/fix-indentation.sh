#!/bin/bash

# Script pour corriger l'erreur d'indentation dans config.py
# Cette erreur se produit dans le conteneur Docker

echo "Correction de l'erreur d'indentation dans config.py..."

# Accéder au répertoire du service job-parser
cd /app

# Vérifier si le fichier config.py existe
if [ -f "/app/app/core/config.py" ]; then
  echo "Fichier config.py trouvé, application de la correction..."
  
  # Corriger l'indentation du bloc try
  sed -i '24s/try:/try:/' /app/app/core/config.py
  sed -i '25s/from/    from/' /app/app/core/config.py
  sed -i '26s/from/    from/' /app/app/core/config.py
  
  echo "Correction appliquée."
else
  echo "Erreur: Le fichier config.py n'a pas été trouvé à l'emplacement attendu."
  exit 1
fi

echo "Vérification et installation de pydantic-settings si nécessaire..."
pip install pydantic-settings

echo "Correction terminée."
