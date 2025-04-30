#!/bin/bash

echo "Redémarrage du service de parsing de fiches de poste"

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher un message formaté
print_status() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Vérification que Docker est disponible
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

# Vérification que docker-compose est disponible
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

# Arrêt des services liés au job parser
print_status "Arrêt des services de parsing de fiches de poste..."
docker-compose stop job-parser job-parser-worker

# Vérifier si on doit nettoyer les conteneurs
if [ "$1" == "--clean" ]; then
    print_status "Nettoyage des conteneurs job-parser..."
    docker-compose rm -f job-parser job-parser-worker
fi

# Reconstruction des images si besoin
if [ "$1" == "--rebuild" ] || [ "$1" == "--clean" ]; then
    print_status "Reconstruction des images job-parser..."
    docker-compose build job-parser job-parser-worker
fi

# Démarrage des services
print_status "Démarrage des services de parsing de fiches de poste..."
docker-compose up -d job-parser job-parser-worker

# Vérification que les services sont bien démarrés
print_status "Vérification de l'état des services..."
sleep 5 # Attendre que les services démarrent

# Vérifier l'état des services
job_parser_status=$(docker-compose ps | grep job-parser | grep -v worker | grep -c "Up" || echo "0")
job_parser_worker_status=$(docker-compose ps | grep job-parser-worker | grep -c "Up" || echo "0")

if [ "$job_parser_status" -gt 0 ] && [ "$job_parser_worker_status" -gt 0 ]; then
    print_success "Les services de parsing de fiches de poste sont démarrés et fonctionnels."
    
    # Récupérer le port exposé
    port=$(docker-compose port job-parser 5000 | cut -d ':' -f 2 || echo "5053")
    print_success "Le service job-parser est accessible sur http://localhost:${port}"
    
    # Tester l'API
    print_status "Test de l'API de santé..."
    health_response=$(curl -s "http://localhost:${port}/health")
    
    if [[ "$health_response" == *"healthy"* ]]; then
        print_success "L'API de santé répond correctement."
        echo -e "${GREEN}==========================================${NC}"
        echo "Pour tester le parsing d'une fiche de poste, utilisez:"
        echo "  ./curl-test-job-parser.sh chemin/vers/fiche.pdf"
        echo -e "${GREEN}==========================================${NC}"
    else
        print_error "L'API de santé ne répond pas correctement."
        print_status "Réponse: $health_response"
    fi
else
    print_error "Problème lors du démarrage des services de parsing de fiches de poste."
    echo "Vérifiez les logs pour plus d'informations:"
    echo "  docker-compose logs job-parser"
    echo "  docker-compose logs job-parser-worker"
fi
