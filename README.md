# Commitment - Parsing et Matching de CV et Fiches de Poste

Ce projet contient les microservices Docker pour le parsing et le matching de CV et fiches de poste.

## Configuration requise

1. **Clé API OpenAI** : Vous devez disposer d'une clé API OpenAI valide pour utiliser les services de parsing.
   - Créez un fichier `.env` à la racine du projet (en vous basant sur `.env.example`)
   - Ajoutez votre clé API OpenAI : `OPENAI=votre_clé_api_openai`

2. **Docker et Docker Compose** : Assurez-vous d'avoir Docker et Docker Compose installés sur votre système.

## Installation rapide

```bash
# Cloner le projet
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-

# Créer le fichier .env
cp .env.example .env
# Éditer .env et ajouter votre clé API OpenAI

# Lancer tous les services
docker-compose up -d
```

## Accès aux services

Après avoir lancé les conteneurs, les services sont accessibles aux URLs suivantes:

- **Frontend**: http://localhost:3000
- **API principale**: http://localhost:5050
- **Service de parsing CV**: http://localhost:5051
- **Service de parsing fiches de poste**: http://localhost:5055 (nouvelle version GPT)
- **Service de matching**: http://localhost:5052
- **MinIO (stockage)**: http://localhost:9000 (API) et http://localhost:9001 (Console)
- **Redis Commander**: http://localhost:8081
- **RQ Dashboard**: http://localhost:9181

## Scripts utilitaires

Le projet contient plusieurs scripts utilitaires pour faciliter le développement:

- `./build_all.sh`: Script pour reconstruire tous les services
- `./restart-cv-parser.sh`: Script pour redémarrer uniquement le service cv-parser
- `./curl-test-cv-parser.sh`: Script pour tester l'API de parsing de CV avec curl
- `./curl-test-job-parser.sh`: Script pour tester l'API de parsing de fiches de poste avec curl

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

## Tester le service de parsing de fiches de poste

Pour tester manuellement le service de parsing de fiches de poste avec GPT:

```bash
# Tester le endpoint health
curl http://localhost:5055/api/health

# Tester le parsing d'une fiche de poste
curl -X POST \
  http://localhost:5055/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/votre/fiche_poste.pdf"
```

## Démarrer le service de parsing de fiches de poste

Le nouveau service de parsing de fiches de poste avec GPT se trouve dans le répertoire `backend/`. Vous pouvez le démarrer de plusieurs façons :

### 1. Utiliser Docker Compose (recommandé)

```bash
# Se placer dans le répertoire backend
cd backend

# Créer le fichier .env à partir du modèle
cp .env.example .env
# Éditer .env et ajouter votre clé API OpenAI

# Démarrer le conteneur
docker compose up -d
```

### 2. Installer et exécuter directement en Python

```bash
# Se placer dans le répertoire backend
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Définir la clé API OpenAI
export OPENAI_API_KEY=votre_clé_api_openai  # Linux/Mac
# ou
set OPENAI_API_KEY=votre_clé_api_openai  # Windows

# Démarrer le serveur
python job_parser_api.py
```

## Utiliser le frontend avec le parser GPT

Pour utiliser le frontend avec le nouveau service de parsing GPT, ouvrez la page web suivante :

```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?apiUrl=http://localhost:5055
```

Ou si vous hébergez le service sur un autre serveur :

```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?apiUrl=http://votre-serveur:5055
```

## Architecture

Le projet utilise une architecture microservices avec les composants suivants :

1. **Service de parsing CV** : Extrait les informations des CV en utilisant GPT-4o-mini
2. **Service de parsing de fiches de poste** : Extrait les informations des offres d'emploi en utilisant GPT-3.5-turbo/GPT-4
3. **Service de matching** : Match les CV avec les offres d'emploi
4. **Redis** : File d'attente pour le traitement asynchrone et cache
5. **MinIO** : Stockage des fichiers (CV et fiches de poste)
6. **PostgreSQL** : Base de données principale
