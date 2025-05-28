# Commitment - Parsing et Matching de CV et Fiches de Poste

Ce projet contient les microservices Docker pour le parsing et le matching de CV et fiches de poste.

## Configuration requise

1. **Clé API OpenAI** : Vous devez disposer d'une clé API OpenAI valide pour utiliser les services de parsing.
   - Créez un fichier `.env` à la racine du projet (en vous basant sur `.env.example`)
   - Ajoutez votre clé API OpenAI : `OPENAI=votre_clé_api_openai`

2. **Clé API Google Maps** (optionnelle mais recommandée) : Pour les fonctionnalités de géolocalisation avancées de SuperSmartMatch.
   - Obtenez votre clé sur [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Ajoutez dans `.env` : `GOOGLE_MAPS_API_KEY=votre_clé_google_maps`

3. **Docker et Docker Compose** : Assurez-vous d'avoir Docker et Docker Compose installés sur votre système.

## Installation rapide

```bash
# Cloner le projet
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-

# Configuration automatique (recommandée)
chmod +x setup-supersmartmatch.sh
./setup-supersmartmatch.sh

# OU configuration manuelle
cp .env.example .env
# Éditer .env et ajouter vos clés API

# Lancer tous les services
chmod +x start-all-services.sh
./start-all-services.sh
```

## Accès aux services

Après avoir lancé les conteneurs, les services sont accessibles aux URLs suivantes:

- **Frontend**: http://localhost:3000
- **API principale**: http://localhost:5050
- **Service de parsing CV**: http://localhost:5051
- **Service de parsing fiches de poste**: http://localhost:5055 (nouvelle version GPT)
- **Service de matching**: http://localhost:5052
- **🚀 SuperSmartMatch**: http://localhost:5062 (algorithme de matching intelligent)
- **Service d'analyse comportementale**: http://localhost:5057
- **Service de personnalisation**: http://localhost:5060
- **MinIO (stockage)**: http://localhost:9000 (API) et http://localhost:9001 (Console)
- **Redis Commander**: http://localhost:8081
- **RQ Dashboard**: http://localhost:9181

## 🚀 SuperSmartMatch - Algorithme de Matching Intelligent

SuperSmartMatch est notre algorithme de matching de nouvelle génération qui propose :

### ✨ Fonctionnalités principales
- **🗺️ Géolocalisation précise** : Calcul de temps de trajet en temps réel avec Google Maps
- **🧠 Raisonnement intelligent** : Matching basé sur la logique métier (évolution, stabilité, innovation)
- **📊 Scoring détaillé** : Pourcentages par critère pour les entreprises
- **⚡ Multiple algorithmes** : 5 algorithmes disponibles avec sélection automatique

### 🎯 Algorithmes disponibles

1. **`auto`** - Sélection automatique optimale ⭐ (recommandé)
2. **`smart-match`** - Matching géographique avec Google Maps 
3. **`enhanced`** - Pondération adaptative intelligente
4. **`semantic`** - Analyse sémantique des compétences  
5. **`hybrid`** - Combinaison de plusieurs algorithmes

### 🚀 Configuration rapide de SuperSmartMatch

```bash
# Script de configuration automatique
chmod +x setup-supersmartmatch.sh
./setup-supersmartmatch.sh

# Test du service
curl http://localhost:5062/api/v1/health

# Test de matching avec géolocalisation
curl -X POST http://localhost:5062/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Python"], "localisation": "Paris"},
    "job_data": [{"id": "1", "competences": ["Python"], "localisation": "Marseille"}],
    "algorithm": "smart-match"
  }'
```

### 📊 Dashboard SuperSmartMatch

Accédez au dashboard de monitoring : **http://localhost:5062/dashboard**

### 🔧 Configuration Google Maps API

Pour activer les fonctionnalités de géolocalisation avancées :

1. **Obtenez une clé API** sur [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. **Activez les APIs** : Geocoding API, Distance Matrix API, Maps JavaScript API
3. **Configurez votre clé** :
   ```bash
   echo "GOOGLE_MAPS_API_KEY=votre-clé-api" >> .env
   docker-compose restart supersmartmatch-service
   ```

Pour plus de détails, consultez le [Guide Google Maps API](GOOGLE_MAPS_SETUP_GUIDE.md).

### 🧪 Tests SuperSmartMatch

```bash
# Test complet de tous les algorithmes
chmod +x test-supersmartmatch.sh
./test-supersmartmatch.sh

# Test spécifique de géolocalisation
chmod +x test-geolocalisation.sh
./test-geolocalisation.sh
```

## Nouvelle fonctionnalité : Personnalisation du matching

Nous avons ajouté un nouveau service de personnalisation qui adapte les résultats de matching en fonction des préférences et du comportement des utilisateurs. Ce service permet de :

- Personnaliser les poids de matching pour chaque utilisateur
- Réordonner les résultats de recherche selon les préférences individuelles
- Gérer les feedbacks utilisateur pour améliorer les recommandations
- Détecter les changements de préférences au fil du temps
- Résoudre le problème du démarrage à froid pour les nouveaux utilisateurs

### Démarrer le service de personnalisation

Le service est normalement démarré avec les autres services via le script `start-all-services.sh`, mais vous pouvez le démarrer individuellement :

```bash
# Rendre le script exécutable
chmod +x personalization-service/start-personalization.sh

# Démarrer le service
cd personalization-service
./start-personalization.sh
```

### Tester le service de personnalisation

```bash
# Rendre le script de test exécutable
chmod +x personalization-service/test-personalization.sh

# Exécuter les tests
./test-personalization.sh
```

### Utiliser l'API de personnalisation

```bash
# Vérifier que le service est actif
curl http://localhost:5060/health

# Obtenir des poids de matching personnalisés
curl -X POST http://localhost:5060/api/v1/personalize/matching \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "job_id": 456,
    "original_weights": {
      "skills": 0.4,
      "experience": 0.3,
      "education": 0.2,
      "certifications": 0.1
    }
  }'
```

Pour plus de détails, consultez le [Guide de test du service de personnalisation](personalization-service/TEST-GUIDE.md).

## Nouvelle fonctionnalité : Analyse comportementale et profiling utilisateur

Nous avons ajouté un service pour l'analyse comportementale et le profiling utilisateur. Ce service permet de :

- Créer des profils utilisateur enrichis basés sur leur comportement
- Segmenter automatiquement les utilisateurs via des algorithmes de clustering
- Détecter les patterns comportementaux récurrents
- Calculer des scores de préférence dynamiques pour personnaliser l'expérience

### Démarrer le service d'analyse comportementale

```bash
# Le service est normalement démarré via Docker Compose avec le script start-all-services.sh
```

### Utiliser l'API d'analyse comportementale

```bash
# Vérifier que le service est actif
curl http://localhost:5057/health

# Créer un profil utilisateur
curl -X POST http://localhost:5057/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "John Doe",
    "interactions": [
      {
        "user_id": "user123",
        "action_type": "view_job",
        "timestamp": "2025-05-20T10:00:00Z",
        "item_id": "job-123",
        "job_category": "Development"
      }
    ]
  }'
```

Pour plus de détails, consultez le [Guide d'utilisation de l'analyse comportementale](user-behavior-guide.md).

## Nouvelle fonctionnalité : Analyse GPT des fiches de poste

Nous avons ajouté un nouveau service d'analyse des fiches de poste avec GPT. Ce service permet d'extraire automatiquement les informations clés des fiches de poste, comme le titre, l'entreprise, la localisation, les compétences requises, etc.

### Démarrer le service d'analyse GPT des fiches de poste

```bash
# Se placer dans le répertoire job-parser-service
cd job-parser-service

# Rendre le script de démarrage exécutable
chmod +x start-gpt-api.sh

# Démarrer le service
./start-gpt-api.sh
```

Vous serez invité à saisir votre clé API OpenAI si elle n'est pas déjà définie dans l'environnement.

### Utiliser Docker pour le service d'analyse GPT

```bash
# Se placer dans le répertoire job-parser-service
cd job-parser-service

# Construire l'image Docker
docker build -t job-parser-gpt-api .

# Démarrer le conteneur
docker run -p 5055:5055 -e OPENAI_API_KEY="votre-clé-api-openai" job-parser-gpt-api
```

### Utiliser le frontend avec l'analyse GPT

Pour utiliser l'interface web avec le nouveau service d'analyse GPT, ouvrez la page suivante :

```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?apiUrl=http://localhost:5055
```

Vous pouvez également ajouter le paramètre `debug=true` pour activer le mode de débogage :

```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?apiUrl=http://localhost:5055&debug=true
```

## Scripts utilitaires

Le projet contient plusieurs scripts utilitaires pour faciliter le développement:

- `./setup-supersmartmatch.sh`: **Configuration automatique de SuperSmartMatch** (recommandé)
- `./start-all-services.sh`: Script pour démarrer tous les services
- `./test-supersmartmatch.sh`: Script pour tester SuperSmartMatch complet
- `./build_all.sh`: Script pour reconstruire tous les services
- `./restart-cv-parser.sh`: Script pour redémarrer uniquement le service cv-parser
- `./curl-test-cv-parser.sh`: Script pour tester l'API de parsing de CV avec curl
- `./curl-test-job-parser.sh`: Script pour tester l'API de parsing de fiches de poste avec curl
- `./job-parser-service/start-gpt-api.sh`: Script pour démarrer le service d'analyse GPT des fiches de poste
- `./personalization-service/start-personalization.sh`: Script pour démarrer le service de personnalisation
- `./personalization-service/test-personalization.sh`: Script pour tester le service de personnalisation

## Tester le service de parsing CV

Pour tester manuellement le service de parsing CV:

```bash
# Tester le endpoint health
curl http://localhost:5051/health

# Tester le parsing d'un CV
curl -X POST \
  http://localhost:5051/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/votre/cv.pdf" \
  -F "force_refresh=false"
```

## Tester le service d'analyse GPT des fiches de poste

Pour tester manuellement le service d'analyse GPT des fiches de poste:

```bash
# Tester le endpoint health
curl http://localhost:5055/health

# Tester l'analyse par texte
curl -X POST \
  http://localhost:5055/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Fiche de poste: Développeur Full Stack..."}'

# Tester l'analyse par fichier
curl -X POST \
  http://localhost:5055/analyze-file \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/votre/fiche_poste.pdf"
```

## Architecture

Le projet utilise une architecture microservices avec les composants suivants :

1. **Service de parsing CV** : Extrait les informations des CV en utilisant GPT-4o-mini
2. **Service de parsing de fiches de poste** : Extrait les informations des offres d'emploi en utilisant GPT-3.5-turbo/GPT-4
3. **Service de matching** : Match les CV avec les offres d'emploi
4. **🚀 SuperSmartMatch** : Algorithme de matching intelligent avec géolocalisation
5. **Service d'analyse comportementale** : Crée des profils utilisateur enrichis et analyse le comportement
6. **Service de personnalisation** : Adapte les résultats selon les préférences utilisateur
7. **Redis** : File d'attente pour le traitement asynchrone et cache
8. **MinIO** : Stockage des fichiers (CV et fiches de poste)
9. **PostgreSQL** : Base de données principale

## 📚 Documentation

- **[Guide SuperSmartMatch](GUIDE-SUPERSMARTMATCH.md)** : Documentation complète de l'algorithme
- **[Configuration Google Maps](GOOGLE_MAPS_SETUP_GUIDE.md)** : Guide de configuration Google Maps API
- **[Guide d'intégration SuperSmartMatch](SUPERSMARTMATCH-INTEGRATION-GUIDE.md)** : Intégration dans vos projets

## Résolution des problèmes courants

### Problèmes de ports utilisés

Si vous rencontrez des erreurs indiquant que des ports sont déjà utilisés, vous pouvez :

```bash
# Arrêter tous les conteneurs Docker en cours d'exécution
docker-compose down

# Identifier les processus qui utilisent les ports
lsof -i :5060  # Pour le service de personnalisation
lsof -i :5057  # Pour le service d'analyse comportementale
lsof -i :5062  # Pour SuperSmartMatch

# Arrêter les processus identifiés
kill <PID>
```

### Problèmes de connexion à Redis

Si le service de personnalisation ne peut pas se connecter à Redis :

```bash
# Vérifier que le conteneur Redis est en cours d'exécution
docker ps | grep redis

# Vérifier les logs du conteneur Redis
docker logs nexten-redis

# Tester la connexion à Redis manuellement
docker exec -it nexten-redis redis-cli ping
```

### Problèmes Google Maps API (SuperSmartMatch)

Si SuperSmartMatch ne peut pas utiliser Google Maps :

```bash
# Vérifier que la clé est configurée
grep GOOGLE_MAPS_API_KEY .env

# Tester la clé directement
curl "https://maps.googleapis.com/maps/api/geocode/json?address=Paris&key=votre-clé"

# Redémarrer SuperSmartMatch
docker-compose restart supersmartmatch-service

# Vérifier les logs
docker logs nexten-supersmartmatch | grep -i "google\|maps"
```

## 🎯 Démarrage rapide SuperSmartMatch

```bash
# Configuration automatique complète
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-
chmod +x setup-supersmartmatch.sh
./setup-supersmartmatch.sh

# Test immédiat
curl http://localhost:5062/api/v1/health
open http://localhost:5062/dashboard
```
