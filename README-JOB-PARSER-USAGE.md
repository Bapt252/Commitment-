# Guide d'Utilisation et de Dépannage du Job Parser

Ce document explique comment utiliser et dépanner le service job-parser pour l'analyse des fiches de poste.

## Installation et Démarrage

Pour démarrer le service :

```bash
# Démarrer le service
docker-compose up -d job-parser

# Vérifier que le service est en cours d'exécution
docker-compose ps
```

## Correction des Erreurs Courantes

Deux erreurs courantes peuvent survenir lors du démarrage du service :

### 1. Erreur d'Indentation dans config.py

**Symptôme :** `IndentationError: expected an indented block after 'try' statement on line 24`

**Solution :**
```bash
# Télécharger et exécuter le script de correction
curl -o fix-job-parser-fixed.sh https://raw.githubusercontent.com/Bapt252/Commitment-/main/fix-job-parser-fixed.sh
chmod +x fix-job-parser-fixed.sh
./fix-job-parser-fixed.sh
```

### 2. Erreur de Configuration de Journalisation

**Symptôme :** `AttributeError: 'Settings' object has no attribute 'LOG_DIR'`

**Solution :**
```bash
# Télécharger et exécuter le script de correction directe
curl -o direct-fix-log-dir.sh https://raw.githubusercontent.com/Bapt252/Commitment-/main/direct-fix-log-dir.sh
chmod +x direct-fix-log-dir.sh
./direct-fix-log-dir.sh
```

## Test du Service

Pour tester rapidement le service avec un exemple de fiche de poste :

```bash
# Télécharger et exécuter le script de test
curl -o test-job-parser.sh https://raw.githubusercontent.com/Bapt252/Commitment-/main/test-job-parser.sh
chmod +x test-job-parser.sh
./test-job-parser.sh
```

Ce script crée automatiquement un fichier d'exemple et le soumet à l'API.

## Utilisation de l'API

L'API du service job-parser est accessible à l'adresse http://localhost:5053/api.

### Points d'Entrée Principaux

- **Analyse d'une fiche de poste** : `POST /api/parse-job`
  ```bash
  curl -X POST \
    http://localhost:5053/api/parse-job \
    -H "Content-Type: multipart/form-data" \
    -F "file=@/chemin/vers/votre/fiche_de_poste.pdf" \
    -F "force_refresh=false"
  ```

- **Vérification de l'état du service** : `GET /health`
  ```bash
  curl http://localhost:5053/health
  ```

### Types de Fichiers Supportés

- PDF (`.pdf`)
- Microsoft Word (`.doc`, `.docx`)
- Texte (`.txt`)
- Rich Text Format (`.rtf`)

## Surveillance et Journalisation

Pour surveiller les logs du service :

```bash
# Afficher les derniers logs
docker-compose logs --tail=20 job-parser

# Suivre les logs en temps réel
docker-compose logs -f job-parser
```

## Dépannage Avancé

Si les scripts de correction ne résolvent pas le problème, essayez les opérations suivantes :

1. **Reconstruire complètement l'image** :
   ```bash
   docker-compose stop job-parser
   docker-compose rm -f job-parser
   docker-compose build --no-cache job-parser
   docker-compose up -d job-parser
   ```

2. **Vérifier les configurations dans le conteneur** :
   ```bash
   # Entrer dans le conteneur
   docker exec -it nexten-job-parser bash
   
   # Vérifier le contenu du fichier config.py
   cat /app/app/core/config.py
   
   # Vérifier la présence du répertoire de logs
   ls -la /app/logs
   ```

3. **Nettoyer les volumes et caches Docker** :
   ```bash
   docker-compose down -v
   docker system prune -f
   ```

## Contribution

Pour contribuer au projet, consultez les fichiers README et CONTRIBUTING à la racine du dépôt.
