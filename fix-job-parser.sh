#!/bin/bash

# Script pour réparer le job-parser, finaliser le merge et configurer l'environnement
# Créé par Claude via GitHub API

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "\n${BLUE}[ÉTAPE]${NC} $1"
    echo "================================================================================"
}

# Déterminer la branche actuelle
CURRENT_BRANCH=$(git branch --show-current)
print_status "Branche actuelle: $CURRENT_BRANCH"

# Étape 1: Vérifier et corriger le fichier .env
print_step "1. Vérification et correction du fichier .env"

if grep -q "<<<<<<< HEAD" .env 2>/dev/null; then
    print_error "Conflit Git détecté dans le fichier .env. Création d'une sauvegarde et correction..."
    # Sauvegarde du fichier original
    cp .env .env.conflict.bak
    
    # Création d'un nouveau fichier .env propre
    cat > .env << 'EOF'
# Configuration pour le service de parsing CV et fiches de poste
# Remplacez par votre propre clé API OpenAI
OPENAI=sk-your-openai-api-key
OPENAI_API_KEY=sk-your-openai-api-key

# Utilisation du mock parser si vous n'avez pas de clé API OpenAI
# Pour un parsing réel, mettez cette valeur à false
USE_MOCK_PARSER=false

# Configuration de base de données
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/nexten

# Redis configuration 
REDIS_URL=redis://redis:6379/0

# MinIO configuration
MINIO_ENDPOINT=storage:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Configuration webhook (optionnelle)
WEBHOOK_SECRET=your-webhook-secret-here

# Google Maps API Key (optionnelle)
GOOGLE_MAPS_API_KEY=
GOOGLE_MAPS_API_KEY_CLIENT=
EOF
    print_success "Fichier .env corrigé et sauvegardé."
else
    print_success "Fichier .env semble valide (pas de marqueurs de conflit détectés)."
fi

# Étape 2: Finalisation du merge en cours si nécessaire
print_step "2. Finalisation du merge Git en cours (si nécessaire)"

MERGE_HEAD_EXISTS=$(test -f .git/MERGE_HEAD && echo "true" || echo "false")

if [ "$MERGE_HEAD_EXISTS" = "true" ]; then
    print_status "Fusion Git en cours détectée, finalisation..."
    
    # Ajouter tous les fichiers résolus
    git add -A
    
    # Finaliser le merge
    git commit -m "Résolution des conflits de fusion et correction du .env pour job-parser"
    
    print_success "Fusion Git finalisée."
else
    print_status "Aucune fusion Git en cours détectée, aucune action nécessaire."
fi

# Étape 3: Création des scripts pour le job-parser
print_step "3. Création des scripts pour le job-parser"

# Script de redémarrage
cat > restart-job-parser.sh << 'EOF'
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
EOF

# Rendre exécutables
chmod +x restart-job-parser.sh
chmod +x curl-test-job-parser.sh

print_success "Scripts job-parser créés et rendus exécutables."

# Étape 4: Commit et push des changements locaux
print_step "4. Commit et push des changements locaux"

# Ajouter les nouveaux fichiers
git add restart-job-parser.sh

# Voir s'il y a des changements à committer
if git diff-index --quiet HEAD --; then
    print_status "Aucun changement détecté, pas besoin de commit."
else 
    # Commit des changements
    git commit -m "Ajout du script restart-job-parser.sh pour simplifier l'utilisation du service"
    print_success "Changements commités localement."
    
    # Push des changements
    print_status "Tentative de push des changements..."
    if git push; then
        print_success "Changements pushés avec succès."
    else
        print_error "Erreur lors du push des changements."
        print_status "Vous pouvez essayer de pusher manuellement plus tard avec 'git push'."
    fi
fi

# Étape 5: Démarrage des services
print_step "5. Démarrage des services job-parser"

print_status "Démarrage des services job-parser..."
./restart-job-parser.sh --clean

print_step "Terminé!"
echo "Le service job-parser devrait maintenant être opérationnel."
echo "Utilisez ./curl-test-job-parser.sh pour tester avec un fichier de fiche de poste."
