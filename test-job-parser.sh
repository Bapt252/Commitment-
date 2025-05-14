#!/bin/bash

# Script pour tester le service job-parser avec un fichier d'exemple

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

# Vérifier si le conteneur est en cours d'exécution
if ! docker ps | grep -q nexten-job-parser; then
  log_error "Le conteneur nexten-job-parser n'est pas en cours d'exécution."
  log_info "Veuillez d'abord démarrer le service job-parser avec docker-compose up -d job-parser."
  exit 1
fi

# Créer un fichier temporaire avec une fiche de poste d'exemple
log_info "Création d'un fichier de fiche de poste d'exemple..."
cat > /tmp/exemple_fiche_poste.txt << 'EOL'
# Fiche de Poste: Développeur Full Stack

## Informations Générales
- Titre du poste: Développeur Full Stack
- Département: Développement
- Localisation: Paris, France
- Type de contrat: CDI
- Date de début: Immédiat

## Description du Poste
Nous recherchons un développeur Full Stack expérimenté pour rejoindre notre équipe de développement. Le candidat idéal sera responsable de la conception, du développement et de la maintenance de nos applications web.

## Responsabilités
- Développer des applications web robustes et évolutives
- Collaborer avec les équipes produit et design
- Participer aux revues de code et aux sessions de planification
- Contribuer à l'amélioration continue de nos processus de développement
- Résoudre les problèmes techniques complexes

## Compétences Techniques
- Maîtrise de JavaScript/TypeScript, React et Node.js
- Expérience avec Python et Django
- Connaissance des bases de données SQL et NoSQL
- Compréhension des principes DevOps et CI/CD
- Expérience avec Docker et Kubernetes

## Qualifications
- Diplôme en informatique ou domaine connexe
- Minimum 3 ans d'expérience en développement web
- Bon niveau d'anglais technique

## Avantages
- Salaire compétitif
- Télétravail partiel
- Formation continue et conférences
- Événements d'entreprise réguliers
- Assurance santé et prévoyance

Pour postuler, envoyez votre CV et lettre de motivation à careers@example.com
EOL

log_info "Fichier créé à /tmp/exemple_fiche_poste.txt"

# Tester l'API avec le fichier d'exemple
log_info "Test de l'API job-parser avec le fichier d'exemple..."

# Vérifier si curl est installé
if ! command -v curl &> /dev/null; then
  log_error "curl n'est pas installé. Veuillez installer curl pour continuer."
  exit 1
fi

# Envoyer la requête
response=$(curl -s -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/exemple_fiche_poste.txt" \
  -F "force_refresh=false")

# Vérifier si la requête a réussi
if [ $? -eq 0 ]; then
  log_success "Requête envoyée avec succès."
  
  # Afficher la réponse de manière formatée
  echo -e "\n\033[0;36m--- Réponse de l'API ---\033[0m"
  echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
  echo -e "\033[0;36m-----------------------\033[0m\n"
else
  log_error "Échec de la requête."
  echo "$response"
fi

# Nettoyer le fichier temporaire
rm /tmp/exemple_fiche_poste.txt

log_info "Test terminé."
