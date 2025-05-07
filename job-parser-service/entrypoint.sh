#!/bin/bash
set -e

# Script de démarrage pour le service job-parser

# Vérifier et corriger l'importation de BaseSettings dans config.py
echo "Vérification et correction de l'importation dans config.py..."
python3 -c '
import os

file_path = "/app/app/core/config.py"
with open(file_path, "r") as f:
    content = f.read()

# Vérifier si la correction est nécessaire
if "from pydantic import BaseSettings" in content and not "from pydantic_settings import BaseSettings" in content:
    print("Correction de l\'importation BaseSettings...")
    # Remplacer l\'importation problématique
    content = content.replace(
        "from pydantic import BaseSettings, validator",
        "try:\n    from pydantic_settings import BaseSettings\n    from pydantic import validator\nexcept ImportError:\n    from pydantic import BaseSettings, validator"
    )
    
    # Écrire le contenu corrigé
    with open(file_path, "w") as f:
        f.write(content)
    print("Correction terminée !")
else:
    print("Importation déjà corrigée ou utilisant une autre structure.")
'

# Vérifier si pydantic-settings est installé
pip install --no-cache-dir pydantic-settings>=2.0.0

# Activer le mode mock si pas de clé OpenAI
if [ -z "${OPENAI_API_KEY}" ] && [ -z "${OPENAI}" ]; then
    echo "Aucune clé API OpenAI trouvée. Activation du mode simulation..."
    export USE_MOCK_PARSER=true
fi

# Exécuter la commande fournie
exec "$@"
