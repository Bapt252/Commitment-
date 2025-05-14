#!/bin/bash

# Script de diagnostic complet pour le service job-parser

# Fonction pour afficher des messages avec couleurs
log_info() {
  echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
  echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_error() {
  echo -e "\033[0;31m[ERROR]\033[0m $1"
}

log_warn() {
  echo -e "\033[0;33m[WARNING]\033[0m $1"
}

log_title() {
  echo -e "\n\033[1;36m=== $1 ===\033[0m\n"
}

# Créer un répertoire pour les fichiers de test
TEST_DIR=$(mktemp -d)
log_info "Fichiers de test créés dans $TEST_DIR"

# Vérifier l'état des containers
log_title "VÉRIFICATION DES CONTAINERS"
log_info "Liste des containers en cours d'exécution :"
docker ps

# Vérifier si le service job-parser est en cours d'exécution
if docker ps | grep -q nexten-job-parser; then
  log_success "Le service job-parser est en cours d'exécution."
else
  log_error "Le service job-parser n'est pas en cours d'exécution."
  log_info "Tentative de démarrage du service..."
  docker-compose up -d job-parser
  sleep 5
  
  if docker ps | grep -q nexten-job-parser; then
    log_success "Le service job-parser a été démarré avec succès."
  else
    log_error "Impossible de démarrer le service job-parser."
    log_info "Vérification des logs de docker-compose..."
    docker-compose logs job-parser
    exit 1
  fi
fi

# Examiner les logs du service
log_title "EXAMEN DES LOGS"
log_info "Dernières entrées des logs du service job-parser :"
docker-compose logs --tail=30 job-parser

# Vérifier l'accessibilité du service
log_title "VÉRIFICATION DE L'ACCESSIBILITÉ"
log_info "Test de la connectivité au service..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5053/health 2>/dev/null | grep -q "200"; then
  log_success "Le service est accessible via l'endpoint /health."
else
  log_warn "L'endpoint /health n'est pas accessible."
  log_info "Vérification de l'accessibilité du port..."
  if nc -z localhost 5053; then
    log_success "Le port 5053 est ouvert et accessible."
  else
    log_error "Le port 5053 n'est pas accessible."
    log_info "Vérification de la configuration des ports..."
    docker-compose ps
    log_info "Vérification des ports exposés..."
    docker inspect nexten-job-parser | grep HostPort
    exit 1
  fi
fi

# Créer un fichier texte très simple pour tester
log_title "TEST AVEC UN FICHIER TEXTE SIMPLE"
log_info "Création d'un fichier texte simple..."
echo "Titre: Développeur Python" > "$TEST_DIR/simple_job.txt"

log_info "Test de l'API avec le fichier texte simple..."
curl -v -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$TEST_DIR/simple_job.txt" \
  -F "force_refresh=false"

# Inspecter le conteneur pour voir les erreurs potentielles
log_title "INSPECTION DU CONTENEUR"
log_info "Vérification des logs du conteneur..."
docker logs nexten-job-parser

log_info "Inspection de la configuration du conteneur..."
docker exec nexten-job-parser bash -c 'cat /app/app/core/config.py | grep LOG_DIR'

log_info "Vérification des répertoires dans le conteneur..."
docker exec nexten-job-parser bash -c 'ls -la /app/logs'

# Créer un script de diagnostic pour le conteneur
log_title "SCRIPT DE DIAGNOSTIC DANS LE CONTENEUR"
log_info "Création d'un script de diagnostic dans le conteneur..."

cat > "$TEST_DIR/diagnose_container.sh" << 'EOL'
#!/bin/bash

echo "=== DIAGNOSTIC DU CONTENEUR ==="
echo "Vérification de l'environnement Python..."
python --version
pip list | grep pydantic

echo "Vérification des variables d'environnement..."
printenv | grep -E 'LOG_|OPENAI'

echo "Vérification de la structure des répertoires..."
ls -la /app
ls -la /app/app
ls -la /app/app/core
ls -la /app/logs

echo "Vérification des permissions..."
id
whoami

echo "Vérification des routes API..."
python -c "
import sys
sys.path.append('/app')
try:
    from app.main import app
    print('Routes disponibles:')
    for route in app.routes:
        print(f'  {route.path} - {route.methods}')
except Exception as e:
    print(f'Erreur: {e}')
"

echo "=== FIN DU DIAGNOSTIC ==="
EOL

# Copier et exécuter le script de diagnostic dans le conteneur
log_info "Exécution du script de diagnostic dans le conteneur..."
docker cp "$TEST_DIR/diagnose_container.sh" nexten-job-parser:/tmp/
docker exec nexten-job-parser bash -c 'chmod +x /tmp/diagnose_container.sh && /tmp/diagnose_container.sh'

# Test avec le fichier PDF du bureau
log_title "TEST AVEC LE FICHIER PDF DU BUREAU"

# Déterminer le chemin du bureau
DESKTOP_PATH="$HOME/Desktop"
if [ ! -d "$DESKTOP_PATH" ]; then
  # Essayer avec Bureau pour les utilisateurs francophones
  DESKTOP_PATH="$HOME/Bureau"
  if [ ! -d "$DESKTOP_PATH" ]; then
    log_error "Impossible de trouver le dossier du bureau (Desktop/Bureau)."
    exit 1
  fi
fi

# Vérifier si le fichier existe
PDF_PATH="$DESKTOP_PATH/fdp.pdf"
if [ ! -f "$PDF_PATH" ]; then
  log_error "Le fichier fdp.pdf n'existe pas sur le bureau."
  log_info "Veuillez vérifier que le fichier existe à l'emplacement : $PDF_PATH"
  exit 1
fi

# Copier le fichier dans le conteneur et tester directement
log_info "Copie du fichier PDF dans le conteneur pour test direct..."
docker cp "$PDF_PATH" nexten-job-parser:/tmp/
docker exec nexten-job-parser bash -c 'ls -la /tmp/fdp.pdf'

# Créer un script de test dans le conteneur
cat > "$TEST_DIR/test_pdf_directly.py" << 'EOL'
import sys
import os
sys.path.append('/app')

# Imprimer le répertoire de travail et le contenu des fichiers importants
print(f"Répertoire de travail : {os.getcwd()}")
print(f"Fichier PDF existe : {os.path.exists('/tmp/fdp.pdf')}")
print(f"Taille du fichier PDF : {os.path.getsize('/tmp/fdp.pdf')} octets")

try:
    # Tenter d'importer les modules nécessaires
    from app.services.parser_service import ParserService
    from app.core.config import settings
    
    # Vérifier les attributs de settings
    print("Configuration settings :")
    for attr in dir(settings):
        if not attr.startswith('_'):
            try:
                value = getattr(settings, attr)
                print(f"  {attr} = {value}")
            except Exception as e:
                print(f"  {attr} = Erreur: {e}")
    
    # Tenter de créer une instance du service
    parser = ParserService()
    print("Service de parsing créé avec succès")
    
    # Tenter de parser le fichier PDF
    print("Tentative de parsing du fichier PDF...")
    result = parser.parse_job_file('/tmp/fdp.pdf')
    print("Résultat du parsing :")
    print(result)
    
except Exception as e:
    print(f"Erreur lors du test : {e}")
    import traceback
    traceback.print_exc()
EOL

# Copier et exécuter le script de test dans le conteneur
log_info "Exécution du test direct dans le conteneur..."
docker cp "$TEST_DIR/test_pdf_directly.py" nexten-job-parser:/tmp/
docker exec nexten-job-parser bash -c 'cd /app && python /tmp/test_pdf_directly.py'

# Test avec l'API cURL
log_info "Test de l'API avec le fichier PDF via cURL..."
curl -v -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$PDF_PATH" \
  -F "force_refresh=false"

# Nettoyage
log_title "NETTOYAGE"
log_info "Suppression des fichiers temporaires..."
rm -rf "$TEST_DIR"

log_success "Diagnostic terminé. Veuillez examiner les résultats ci-dessus pour identifier le problème."
