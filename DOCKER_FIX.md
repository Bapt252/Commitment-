# Guide de réparation des services Docker Nexten

Ce guide détaille les problèmes identifiés dans les services Docker et les solutions appliquées pour résoudre les problèmes de démarrage des conteneurs.

## Problèmes identifiés

### 1. Services `nexten-api`, `cv-parser`, `matching-api` et leurs workers

- **Problème**: Échec au démarrage avec diverses erreurs dans les logs
- **Causes principales**:
  - `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'` avec `openai >= 1.x`
  - Modules `sentence-transformers` non trouvés malgré leur présence dans requirements
  - `fastapi` non installé dans `matching-api` malgré sa présence dans requirements.txt
  - Téléchargement bloqué des modèles ML à la demande (lazy loading)

## Solutions appliquées

### 1. Mise à jour de tous les fichiers `requirements.txt`

Pour chaque service, les fichiers requirements.txt ont été modifiés pour:
- Remettre `openai==0.28.1` (version stable et rétrocompatible)
- Ajouter `torch==2.0.1` juste avant `sentence-transformers==2.2.2`
- Ajouter `httpx==0.24.1` pour les services web
- Réorganiser les dépendances pour éviter les conflits

### 2. Ajout d'un module de compatibilité OpenAI

Dans les services `cv-parser` et `cv-parser-worker`, un module `compat.py` a été créé pour:
- Patcher la bibliothèque `openai` pour injecter une classe `ChatCompletion` si manquante
- Gérer les arguments incompatibles comme `proxies`
- Convertir automatiquement les nouveaux modèles vers ceux supportés par 0.28.1
- Appliquer ce patch dès l'import du module

### 3. Modification des fichiers d'entrée principaux

Dans `main.py` et `worker.py` des services de parsing:
- Ajout de `import compat` tout en haut du fichier pour appliquer le patch avant tout import d'OpenAI

### 4. Amélioration des Dockerfiles

Pour chaque service, les Dockerfiles ont été améliorés pour:
- Installer explicitement `fastapi==0.104.1 uvicorn==0.24.0` dans le service `matching-api`
- Assurer que `openai==0.28.1` est correctement installé via `RUN pip uninstall -y openai && pip install openai==0.28.1`
- Précharger les modèles `sentence-transformers` au moment du build pour éviter les téléchargements dynamiques
- Télécharger les données NLTK nécessaires pendant la construction de l'image

### 5. Scripts de préchargement

Création de scripts `preload_models.py` pour chaque service qui:
- Préchargent les modèles `sentence-transformers`
- Vérifient la compatibilité OpenAI
- Préchargent les modèles spaCy
- Téléchargent les données NLTK
- Vérifient l'installation correcte de FastAPI

## Correction de dépendances spécifiques

- Suppression de `pypdf` au profit de `pdfplumber` qui est plus fiable
- Ajout de `httpx` pour les requêtes HTTP asynchrones
- Assurance que les versions de dépendances sont compatibles entre elles

## Comment reconstruire et démarrer les services

Pour reconstruire tous les services avec les modifications (recommandé):

```bash
# Nettoyer les images et volumes existants
docker-compose down
docker volume prune -f  # Attention: supprime tous les volumes non utilisés

# Reconstruire tous les services sans utiliser le cache
sh ./build_all.sh --force --no-cache
```

Pour reconstruire des services spécifiques:

```bash
# Reconstruire seulement les services API backend
docker-compose build --no-cache api
docker-compose up -d api

# Reconstruire les services cv-parser
docker-compose build --no-cache cv-parser cv-parser-worker
docker-compose up -d cv-parser cv-parser-worker

# Reconstruire les services matching
docker-compose build --no-cache matching-api matching-worker-high matching-worker-standard matching-worker-bulk
docker-compose up -d matching-api matching-worker-high matching-worker-standard matching-worker-bulk
```

## Vérification des services

Pour vérifier que tous les services fonctionnent correctement:

```bash
# Vérifier l'état des conteneurs
docker-compose ps

# Vérifier les logs des services spécifiques
docker logs nexten-api
docker logs nexten-cv-parser
docker logs nexten-matching-api

# Vérifier les healthchecks
docker inspect --format='{{.State.Health.Status}}' nexten-api
docker inspect --format='{{.State.Health.Status}}' nexten-cv-parser
docker inspect --format='{{.State.Health.Status}}' nexten-matching-api
```

## Dépannage supplémentaire

Si des problèmes persistent:

1. **Logs détaillés**: `docker logs <container_id> --tail 100`
2. **Shell dans le conteneur**: `docker exec -it <container_id> /bin/bash`
3. **Vérification des dépendances**: Dans le conteneur, exécutez `pip list | grep <package>` 
4. **Test manuel du modèle**: Utilisez python dans le conteneur pour tester directement un modèle:
   ```bash
   docker exec -it nexten-cv-parser python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print(model.encode('Test'))"
   ```
5. **Vérification réseau**: Assurez-vous que les conteneurs peuvent communiquer entre eux via `docker network inspect nexten-network`

## Résumé des corrections

Ces modifications résolvent les problèmes principaux:
1. **Compatibilité OpenAI**: Downgrade à la version 0.28.1 et correctifs de compatibilité
2. **Dépendances sentence-transformers**: Préchargement et bonne ordre d'installation avec torch
3. **Installation FastAPI**: Installation explicite dans les Dockerfiles
4. **Préchargement modèles**: Modèles chargés au build plutôt qu'au runtime
5. **Suppression de dépendances problématiques**: Remplacement par des alternatives plus fiables

Après ces modifications, tous les services devraient démarrer correctement et être en état "healthy" après un `docker-compose up --build`.