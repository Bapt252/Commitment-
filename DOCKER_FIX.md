# Guide de réparation des services Docker

Ce guide détaille les problèmes identifiés dans les services Docker et les solutions appliquées.

## Problèmes identifiés et corrections

### 1. Service `nexten-api` (restart loop)

**Problème:** Le service API principal dépendait de `sentence-transformers` mais sans les dépendances requises (torch).

**Solution:**
- Ajout de `torch==2.0.1` avant `sentence-transformers` dans `backend/requirements.txt`

### 2. Services `nexten-cv-parser` + `cv-parser-worker` (restart permanent)

**Problème:** Incompatibilité suite au downgrade de `openai` à la version `0.28.1`.

**Solution:**
- Création d'un module de compatibilité `compat.py` qui patche l'API OpenAI pour maintenir la compatibilité
- Modification de `main.py` et `worker.py` pour importer ce module de compatibilité au démarrage

### 3. Service `nexten-matching-api` (crash FastAPI manquant)

**Problème:** Conflit entre Flask et FastAPI, ou problème d'installation de FastAPI.

**Solution:**
- Réorganisation des dépendances dans `matching-service/requirements.txt` (FastAPI en premier)
- Ajout d'une installation explicite de FastAPI dans le Dockerfile avec `RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0`

### 4. Services `matching-worker-*` (tous "unhealthy")

**Problème:** Mêmes problèmes de dépendances que les services précédents.

**Solution:**
- Ajout de torch avant sentence-transformers
- Réorganisation des dépendances pour éviter les conflits

## Comment reconstruire les services

Pour reconstruire tous les services avec les modifications :

```bash
# Reconstruire tous les services
sh ./build_all.sh --force --no-cache
```

Ou pour reconstruire des services spécifiques :

```bash
# Reconstruire seulement l'API
docker-compose build --no-cache api
docker-compose up -d api

# Reconstruire les services cv-parser
docker-compose build --no-cache cv-parser cv-parser-worker
docker-compose up -d cv-parser cv-parser-worker

# Reconstruire les services matching
docker-compose build --no-cache matching-api matching-worker-high matching-worker-standard matching-worker-bulk
docker-compose up -d matching-api
# Attendre que matching-api soit opérationnel
docker-compose up -d matching-worker-high matching-worker-standard matching-worker-bulk
```

## Vérification des services

Pour vérifier que tous les services fonctionnent correctement :

```bash
# Vérifier l'état des conteneurs
docker-compose ps

# Vérifier les logs des services spécifiques
docker logs nexten-api
docker logs nexten-cv-parser
docker logs nexten-matching-api
```

## Dépannage supplémentaire

Si des problèmes persistent :

1. Vérifiez les logs avec `docker logs <container_id>` pour identifier les erreurs spécifiques
2. Assurez-vous que les volumes sont correctement montés
3. Vérifiez que les variables d'environnement sont correctement définies
4. Pour les problèmes de dépendances Python, vous pouvez entrer dans le conteneur avec `docker exec -it <container_id> /bin/bash` et vérifier les packages installés avec `pip list`