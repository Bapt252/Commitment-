# Guide d'installation et de structure du projet Commitment-

Ce guide vous aidera à résoudre les problèmes de structure de dossiers imbriqués et à mettre en place correctement votre environnement de développement.

## Problème identifié

Vous avez actuellement une structure de dossiers fortement imbriquée:
```
~/Commitment-/
  Commitment-/
    Commitment-/
      backend/
        ...
```

Cette imbrication rend difficile la localisation des fichiers et génère des erreurs comme:
```
zsh: no such file or directory: ./reset-api.sh
```

## Solution: Installation propre

Nous avons créé un script qui va mettre en place une structure propre pour vous:

1. **Exécutez le script de nettoyage:**
   ```bash
   chmod +x cleanup-script.sh
   ./cleanup-script.sh
   ```

2. Ce script va:
   - Créer un dossier propre `~/fresh-commitment/`
   - Cloner le dépôt dans ce dossier
   - Rendre tous les scripts exécutables
   - Vous permettre de choisir la branche de travail
   - Récupérer les fichiers manquants si nécessaire

3. **Travaillez dans cette nouvelle structure** au lieu de l'ancienne structure imbriquée.

## Comment éviter ce problème à l'avenir

1. **Ne créez jamais de dossier avec le même nom que le dépôt** avant de cloner.

2. **Utilisez la commande clone correctement:**
   
   ✅ Correcte (crée automatiquement le dossier):
   ```bash
   git clone https://github.com/Bapt252/Commitment-
   ```
   
   ✅ Correcte (clone dans le dossier actuel):
   ```bash
   mkdir mon-projet
   cd mon-projet
   git clone https://github.com/Bapt252/Commitment- .
   ```
   
   ❌ Incorrecte (crée une imbrication):
   ```bash
   mkdir Commitment-
   cd Commitment-
   git clone https://github.com/Bapt252/Commitment-
   ```

## Résolution de problèmes courants

### Script non trouvé (./reset-api.sh)
Si vous obtenez l'erreur "No such file or directory: ./reset-api.sh":

1. **Vérifiez que vous êtes dans le bon dossier**:
   ```bash
   pwd
   # Devrait montrer quelque chose comme /Users/username/fresh-commitment
   ```

2. **Vérifiez si le fichier existe**:
   ```bash
   ls -la
   ```

3. **Si le fichier n'existe pas, récupérez-le**:
   ```bash
   # Depuis la branche principale
   git checkout main -- reset-api.sh
   # OU téléchargez-le directement
   curl -O https://raw.githubusercontent.com/Bapt252/Commitment-/main/reset-api.sh
   chmod +x reset-api.sh
   ```

### ImportError lors de l'exécution de l'API

Si vous rencontrez une erreur comme:
```
ImportError: cannot import name 'JobDescriptionExtractor' from 'app.nlp.job_parser'
```

C'est probablement parce que:
1. Vous travaillez sur une branche de développement où cette classe n'existe pas encore
2. Vous n'avez pas installé toutes les dépendances requises

Solutions:
1. **Vérifiez que vous êtes sur la bonne branche**
2. **Installez les dépendances**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Vérifiez le code** du module `app.nlp.job_parser.py` pour vous assurer que la classe existe

## Structure du projet

Le projet Commitment- est organisé comme suit:
- `backend/` - Contient l'API FastAPI 
- `ml_engine/` - Contient les modèles d'apprentissage automatique
- `static/`, `templates/`, `css/`, `js/` - Contient les fichiers frontend
- Scripts utilitaires à la racine:
  - `reset-api.sh` - Réinitialise l'API
  - `test-api.sh` - Teste les endpoints de l'API
  - `make-scripts-executable.sh` - Donne les permissions d'exécution aux scripts

## Contribution au projet

Si vous travaillez sur la branche `feature-xgboost-matching`, assurez-vous de bien comprendre les modifications en cours. Cette branche contient probablement du code en développement qui pourrait ne pas être entièrement fonctionnel.

Pour revenir à la branche principale:
```bash
git checkout main
```
