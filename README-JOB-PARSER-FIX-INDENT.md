# Correctif pour l'Erreur d'Indentation du Job Parser

Ce document explique comment résoudre l'erreur d'indentation dans le service job-parser qui empêche son démarrage. 

## Problème

L'erreur suivante est observée lors du démarrage du service job-parser :

```
IndentationError: expected an indented block after 'try' statement on line 24
```

Cette erreur se produit dans le fichier `/app/app/core/config.py`, où un bloc `try` à la ligne 24 ne contient pas de code indenté correctement après lui.

## Solution

Nous avons apporté plusieurs correctifs pour résoudre ce problème :

1. **Script de correction d'indentation** : Un nouveau script `fix-indentation.sh` a été ajouté pour corriger l'indentation dans le fichier config.py.

2. **Modification du Dockerfile** : Le Dockerfile a été mis à jour pour installer `pydantic-settings` et rendre nos scripts exécutables.

3. **Mise à jour du script entrypoint.sh** : Le script d'entrée a été modifié pour exécuter automatiquement notre script de correction.

4. **Script de reconstruction** : Un nouveau script `rebuild-job-parser-fixed.sh` a été ajouté pour faciliter la reconstruction et le redémarrage du service avec les corrections.

## Comment utiliser la solution

Pour résoudre le problème, vous avez deux options :

### Option 1 : Utiliser le script de reconstruction

1. Assurez-vous que les modifications sont bien sur votre système (pull du dépôt)
2. Rendez le script exécutable :
   ```bash
   chmod +x rebuild-job-parser-fixed.sh
   ```
3. Exécutez le script :
   ```bash
   ./rebuild-job-parser-fixed.sh
   ```

### Option 2 : Reconstruire manuellement

1. Arrêtez le service job-parser :
   ```bash
   docker-compose stop job-parser
   docker-compose rm -f job-parser
   ```

2. Reconstruisez l'image :
   ```bash
   docker-compose build job-parser
   ```

3. Redémarrez le service :
   ```bash
   docker-compose up -d job-parser
   ```

## Vérification

Après avoir appliqué les correctifs, vérifiez que le service démarre correctement en consultant les logs :

```bash
docker-compose logs job-parser
```

Vous devriez voir un démarrage normal sans l'erreur d'indentation.

## Détails techniques

- Le problème principal était un bloc `try` dans `config.py` qui n'avait pas de contenu indenté après lui.
- Notre solution s'assure que le fichier `config.py` est correctement écrit à chaque démarrage du conteneur.
- Nous avons également ajouté l'installation de `pydantic-settings` dans le processus de build pour garantir sa disponibilité.
