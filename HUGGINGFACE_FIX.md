# Correction des problèmes de compatibilité avec huggingface_hub

## Problème résolu

Une erreur se produisait lors du build Docker avec le message suivant:

```
ImportError: cannot import name 'cached_download' from 'huggingface_hub' (/usr/local/lib/python3.11/site-packages/huggingface_hub/__init__.py)
```

Nous avons également identifié un conflit de dépendances:

```
ERROR: Cannot install -r requirements.txt (line 16), -r requirements.txt (line 19) and huggingface_hub==0.12.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested huggingface_hub==0.12.0
    sentence-transformers 2.2.2 depends on huggingface-hub>=0.4.0
    transformers 4.31.0 depends on huggingface-hub<1.0 and >=0.14.1
```

## Solution appliquée

1. Nous avons mis à jour les versions des packages pour assurer la compatibilité:
   - `huggingface_hub==0.14.1` (au lieu de 0.12.0)
   - `transformers==4.25.1` (au lieu de 4.31.0)
   - `sentence-transformers==2.2.2` (inchangé)

2. Cette combinaison résout le problème car:
   - `huggingface_hub==0.14.1` contient encore la fonction `cached_download`
   - `transformers==4.25.1` est compatible avec `huggingface_hub==0.14.1`
   - `sentence-transformers==2.2.2` est compatible avec les deux

3. Les modifications suivantes ont été effectuées:
   - Mise à jour des fichiers requirements.txt du backend et du matching-service
   - Simplification des Dockerfiles pour mieux gérer les dépendances
   - Ajout de commandes pour vérifier les versions installées

## Comment vérifier que cela fonctionne

Pour reconstruire proprement l'environnement:

1. Rendez le script `rebuild-all.sh` exécutable:
   ```bash
   chmod +x rebuild-all.sh
   ```

2. Exécutez le script pour nettoyer les images Docker et reconstruire:
   ```bash
   ./rebuild-all.sh
   ```

3. Vérifiez les versions installées dans les containers:
   ```bash
   docker exec nexten-api pip freeze | grep huggingface
   docker exec nexten-api pip freeze | grep sentence
   docker exec nexten-api pip freeze | grep transformers
   ```

Vous devriez voir:
- huggingface_hub==0.14.1
- sentence-transformers==2.2.2
- transformers==4.25.1

## Si le problème persiste

Si vous rencontrez toujours des problèmes après un rebuild complet, essayez ces étapes supplémentaires:

1. Supprimer entièrement le cache Docker:
   ```bash
   docker builder prune -a -f
   ```

2. Supprimer tous les volumes associés aux conteneurs:
   ```bash
   docker-compose down -v
   ```

3. Vérifiez s'il n'y a pas d'autres services qui tentent d'installer leurs propres versions:
   ```bash
   grep -r "huggingface\|transformers\|sentence" --include="*.py" --include="*.txt" --include="Dockerfile" .
   ```

## Note de compatibilité

Si vous souhaitez mettre à jour ces bibliothèques à l'avenir, assurez-vous de vérifier la compatibilité. Les versions connues pour être compatibles sont:

- Combinaison actuelle: huggingface_hub==0.14.1, transformers==4.25.1, sentence-transformers==2.2.2
- Alternative 1: huggingface_hub>=0.14.1, transformers==4.31.0, sentence-transformers>=2.2.2
- Alternative 2: huggingface_hub==0.12.0, transformers==4.20.0, sentence-transformers==2.2.2
