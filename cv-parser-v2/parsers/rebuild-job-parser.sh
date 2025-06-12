#!/bin/bash

# Script pour reconstruire et démarrer le service job-parser après les modifications

echo "Reconstruction et démarrage du service job-parser"
echo "================================================="

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

# Récupérer les dernières modifications
print_status "Récupération des dernières modifications depuis GitHub..."
git pull

if [ $? -ne 0 ]; then
    print_error "Erreur lors de la récupération des modifications. Tentative de continuer quand même..."
fi

# Arrêter et supprimer les conteneurs existants
print_status "Arrêt des conteneurs job-parser existants..."
docker-compose stop job-parser job-parser-worker
docker-compose rm -f job-parser job-parser-worker

# Nettoyer les images existantes
print_status "Suppression des images job-parser existantes..."
docker rmi $(docker images | grep job-parser | awk '{print $3}') 2>/dev/null || echo "Aucune image à supprimer"

# Reconstruire les images
print_status "Reconstruction des images job-parser..."
docker-compose build job-parser job-parser-worker

if [ $? -ne 0 ]; then
    print_error "Erreur lors de la reconstruction des images."
    exit 1
fi

# Démarrer les services
print_status "Démarrage des services job-parser..."
docker-compose up -d job-parser job-parser-worker

# Attendre que les services démarrent
print_status "Attente du démarrage des services..."
sleep 5

# Vérifier si les services sont en cours d'exécution
JOB_PARSER_RUNNING=$(docker-compose ps | grep job-parser | grep -v worker | grep -c "Up" || echo "0")
JOB_PARSER_WORKER_RUNNING=$(docker-compose ps | grep job-parser-worker | grep -c "Up" || echo "0")

if [ "$JOB_PARSER_RUNNING" -gt 0 ] && [ "$JOB_PARSER_WORKER_RUNNING" -gt 0 ]; then
    print_success "Les services job-parser sont maintenant en cours d'exécution!"
    
    # Obtenir le port mappé
    PORT=$(docker-compose port job-parser 5000 | cut -d ':' -f 2 || echo "5053")
    
    print_success "Le service job-parser est accessible à l'adresse http://localhost:${PORT}"
    
    # Vérifier que l'API est accessible
    print_status "Test de l'API de santé..."
    HEALTH_RESPONSE=$(curl -s http://localhost:${PORT}/health)
    
    if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
        print_success "L'API de santé répond correctement!"
        echo ""
        echo "Pour tester le service avec une fiche de poste:"
        echo "----------------------------------------------"
        echo "chmod +x curl-test-job-parser.sh"
        echo "./curl-test-job-parser.sh /chemin/vers/votre/fiche_de_poste.pdf"
        echo ""
        echo "Exemple avec fdp.pdf sur le bureau:"
        echo "./curl-test-job-parser.sh ~/Desktop/fdp.pdf"
    else
        print_error "L'API de santé ne répond pas correctement."
        print_status "Réponse: $HEALTH_RESPONSE"
        print_status "Vérifiez les logs avec: docker-compose logs job-parser"
    fi
else
    print_error "Les services job-parser ne sont pas en cours d'exécution."
    print_status "Vérifiez les logs avec: docker-compose logs job-parser"
fi
