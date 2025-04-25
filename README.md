# Commitment - Parsing et Matching de CV

Ce projet contient les microservices Docker pour le parsing et le matching de CV.

## Configuration requise

1. **Clé API OpenAI** : Vous devez disposer d'une clé API OpenAI valide pour utiliser le service de parsing de CV.
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
- **Service de parsing CV**: http://localhost:5051 ou http://localhost:8000
- **Service de matching**: http://localhost:5052
- **MinIO (stockage)**: http://localhost:9000 (API) et http://localhost:9001 (Console)
- **Redis Commander**: http://localhost:8081
- **RQ Dashboard**: http://localhost:9181

## Scripts utilitaires

Le projet contient plusieurs scripts utilitaires pour faciliter le développement:

- `./build_all.sh`: Script pour reconstruire tous les services
- `./restart-cv-parser.sh`: Script pour redémarrer uniquement le service cv-parser
- `./curl-test-cv-parser.sh`: Script pour tester l'API de parsing de CV avec curl

## Tester le service de parsing CV

Pour tester manuellement le service de parsing CV:

```bash
# Tester le endpoint health
curl http://localhost:8000/health

# Tester le parsing d'un CV
curl -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/votre/cv.pdf" \
  -F "force_refresh=false"
```

Ou utilisez le script utilitaire:

```bash
# Assurez-vous que le script est exécutable
chmod +x curl-test-cv-parser.sh

# Exécutez le script (modifiez le chemin du CV dans le script si nécessaire)
./curl-test-cv-parser.sh
```

## Résolution des problèmes courants

### Service cv-parser inaccessible sur le port 8000

Si le service cv-parser n'est pas accessible sur le port 8000, exécutez:

```bash
# Redémarrer le service cv-parser
./restart-cv-parser.sh
```

### Vérifier l'état des services

```bash
# Vérifier l'état de tous les services
docker-compose ps

# Vérifier les logs d'un service spécifique
docker-compose logs cv-parser
```

### Problèmes avec les volumes Docker

Si vous rencontrez des problèmes avec les volumes Docker:

```bash
# Nettoyer les volumes non utilisés (attention: cela supprime les données)
docker volume prune

# Reconstruire les services en préservant les volumes
./build_all.sh --preserve-volumes
```

### Problèmes avec l'API OpenAI

Si vous rencontrez des erreurs liées à l'API OpenAI:

1. Vérifiez que votre clé API est correctement configurée dans le fichier `.env`
2. Assurez-vous que votre clé API est active et a des crédits disponibles
3. Vérifiez les logs du service cv-parser pour plus de détails : `docker-compose logs cv-parser`

## Architecture

Le projet utilise une architecture microservices avec les composants suivants :

1. **Service de parsing CV** : Extrait les informations des CV en utilisant GPT-4o-mini
2. **Service de matching** : Match les CV avec les offres d'emploi
3. **Redis** : File d'attente pour le traitement asynchrone et cache
4. **MinIO** : Stockage des fichiers CV
5. **PostgreSQL** : Base de données principale
