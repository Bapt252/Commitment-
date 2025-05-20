#!/bin/bash
# Script pour initialiser et tester le système de tracking

set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Initialisation du système de tracking ===${NC}"

# Vérifier les dépendances
echo -e "${YELLOW}Vérification des dépendances...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Erreur: Docker n'est pas installé.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Erreur: Docker Compose n'est pas installé.${NC}"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}Attention: psql n'est pas installé. Impossible d'initialiser directement la base de données.${NC}"
fi

# Créer le network Docker si nécessaire
docker network inspect commitment-network &> /dev/null || docker network create commitment-network

# Appliquer le schéma de base de données
echo -e "${YELLOW}Application du schéma de base de données...${NC}"

if command -v psql &> /dev/null; then
    # Obtenir les variables d'environnement PostgreSQL
    DB_HOST=${POSTGRES_HOST:-$(grep POSTGRES_HOST .env | cut -d '=' -f2 || echo "localhost")}
    DB_PORT=${POSTGRES_PORT:-$(grep POSTGRES_PORT .env | cut -d '=' -f2 || echo "5432")}
    DB_USER=${POSTGRES_USER:-$(grep POSTGRES_USER .env | cut -d '=' -f2 || echo "postgres")}
    DB_PASSWORD=${POSTGRES_PASSWORD:-$(grep POSTGRES_PASSWORD .env | cut -d '=' -f2 || echo "postgres")}
    DB_NAME=${POSTGRES_DB:-$(grep POSTGRES_DB .env | cut -d '=' -f2 || echo "commitment")}

    # Tester la connexion
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}Connexion à PostgreSQL réussie.${NC}"
        
        # Appliquer le schéma
        echo -e "${YELLOW}Application du schéma de base...${NC}"
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/08_tracking_schema.sql
        
        echo -e "${YELLOW}Application des extensions...${NC}"
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/08_tracking_extensions.sql
        
        echo -e "${GREEN}Schéma de base de données appliqué avec succès.${NC}"
    else
        echo -e "${RED}Impossible de se connecter à PostgreSQL. Assurez-vous que le serveur est en cours d'exécution.${NC}"
        echo -e "${YELLOW}Le schéma sera appliqué lors du démarrage des conteneurs.${NC}"
    fi
else
    echo -e "${YELLOW}psql n'est pas installé. Le schéma sera appliqué lors du démarrage des conteneurs.${NC}"
fi

# Lancer les services Docker
echo -e "${YELLOW}Lancement des services de tracking...${NC}"
docker-compose -f docker-compose.tracking.yml up -d

echo -e "${GREEN}Services de tracking lancés. Attendez quelques secondes pour qu'ils soient prêts...${NC}"
sleep 5

# Test des API
echo -e "${YELLOW}Test de l'API de tracking...${NC}"

# Test de l'endpoint de santé
HEALTH_RESPONSE=$(curl -s http://localhost:5055/health)
if [ "$HEALTH_RESPONSE" = '{"status":"ok"}' ]; then
    echo -e "${GREEN}API de tracking en ligne et fonctionnelle.${NC}"
else
    echo -e "${RED}Erreur: L'API de tracking ne répond pas correctement.${NC}"
    echo "Réponse: $HEALTH_RESPONSE"
fi

# Test de consentement
echo -e "${YELLOW}Test de l'API de consentement...${NC}"
CONSENT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"user_id":"test_user","consent_type":"analytics","is_granted":true}' http://localhost:5055/api/consent/set)

if [[ "$CONSENT_RESPONSE" == *"success"* ]]; then
    echo -e "${GREEN}Consentement défini avec succès.${NC}"
else
    echo -e "${RED}Erreur lors de la définition du consentement.${NC}"
    echo "Réponse: $CONSENT_RESPONSE"
fi

# Test d'événement
echo -e "${YELLOW}Test de l'API d'événements...${NC}"
EVENT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{
    "event_type": "match_proposed",
    "user_id": "test_user",
    "match_id": "test_match_123",
    "match_score": 85.5,
    "match_parameters": {"skill_weight": 0.7},
    "alternatives_count": 3,
    "constraint_satisfaction": {"skills": 0.9, "location": 0.8}
}' http://localhost:5055/api/events/match/proposed)

if [[ "$EVENT_RESPONSE" == *"accepted"* ]]; then
    echo -e "${GREEN}Événement enregistré avec succès.${NC}"
else
    echo -e "${RED}Erreur lors de l'enregistrement de l'événement.${NC}"
    echo "Réponse: $EVENT_RESPONSE"
fi

# Test d'intégration du client JavaScript
echo -e "${YELLOW}Test d'intégration du client JavaScript...${NC}"

cat > /tmp/test-tracking.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Test de tracking</title>
    <script src="http://localhost:5055/js/tracking-client.js"></script>
</head>
<body>
    <h1>Test de tracking</h1>
    <p>Vérifiez la console pour voir les résultats des tests.</p>
    <script>
        // Initialiser le client de tracking
        const client = new TrackingClient('http://localhost:5055', {
            debug: true,
            batchInterval: 1000
        });
        
        // Enregistrer le consentement
        client.setConsent('test_user_js', 'analytics', true)
            .then(success => {
                console.log('Consentement défini:', success);
                
                // Tracker un événement
                if (success) {
                    client.trackMatchProposed(
                        'test_user_js',
                        'test_match_456',
                        92.5,
                        { "experience_weight": 0.8 },
                        { "skills": 0.95, "location": 0.7 },
                        2
                    );
                    
                    console.log('Événement ajouté à la queue');
                }
            });
    </script>
</body>
</html>
EOF

echo -e "${GREEN}Fichier de test HTML créé: /tmp/test-tracking.html${NC}"
echo -e "${YELLOW}Ouvrez ce fichier dans un navigateur pour tester le client JavaScript.${NC}"

# Test d'accès à Grafana
echo -e "${YELLOW}Test d'accès à Grafana...${NC}"
GRAFANA_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

if [ "$GRAFANA_RESPONSE" = "200" ]; then
    echo -e "${GREEN}Grafana accessible à l'adresse http://localhost:3000${NC}"
    echo -e "${YELLOW}Utilisez les identifiants par défaut: admin/admin${NC}"
else
    echo -e "${RED}Erreur: Grafana n'est pas accessible.${NC}"
fi

echo -e "${GREEN}=== Initialisation du système de tracking terminée ===${NC}"
echo ""
echo -e "${YELLOW}Pour arrêter les services:${NC} docker-compose -f docker-compose.tracking.yml down"
echo -e "${YELLOW}Pour voir les logs:${NC} docker-compose -f docker-compose.tracking.yml logs -f"
echo -e "${YELLOW}Dashboard Grafana:${NC} http://localhost:3000"
echo -e "${YELLOW}API de tracking:${NC} http://localhost:5055"
echo ""
