@echo off
REM start-backend.bat - Script pour démarrer rapidement le backend du job parser sur Windows

REM Vérifier si Python est installé
python --version 2>NUL
if errorlevel 1 (
    echo Python n'est pas installé ou n'est pas dans le PATH. Veuillez l'installer pour continuer.
    exit /b 1
)

REM Vérifier si les dépendances sont installées
python -c "import importlib.util; all(importlib.util.find_spec(m) for m in ['flask', 'flask_cors', 'requests', 'PyPDF2', 'docx'])" 2>NUL
if errorlevel 1 (
    echo Installation des dépendances...
    pip install flask flask-cors requests PyPDF2 python-docx
)

REM Vérifier si la clé API OpenAI est configurée
if "%OPENAI_API_KEY%"=="" (
    echo ATTENTION: Aucune clé API OpenAI n'est configurée.
    echo Le service fonctionnera en mode limité (analyse locale uniquement).
    echo Pour utiliser l'API OpenAI, définissez la variable d'environnement OPENAI_API_KEY.
    echo Exemple: set OPENAI_API_KEY=votre-clé-api
    echo.
)

REM Démarrer le serveur
echo Démarrage du serveur backend...
python job_parser_api.py
