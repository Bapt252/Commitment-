# Correction des problèmes de compatibilité avec huggingface_hub

## Problème résolu

Une erreur se produisait lors du build Docker avec le message suivant:

```
ImportError: cannot import name 'cached_download' from 'huggingface_hub' (/usr/local/lib/python3.11/site-packages/huggingface_hub/__init__.py)
```

Cette erreur est survenue car la fonction `cached_download` a été supprimée ou renommée dans les versions récentes de `huggingface_hub`, mais la version de `sentence-transformers` utilisée (2.2.2) essayait toujours de l'utiliser.

## Solution appliquée

1. La version de `huggingface_hub` a été fixée à 0.12.0 dans tous les services:
   - Dans le service backend (API)
   - Dans le service matching-service

2. Les modifications suivantes ont été effectuées:
   - Mise à jour des Dockerfiles pour forcer l'installation de huggingface_hub==0.12.0
   - Mise à jour des fichiers requirements.txt pour spécifier cette même version

## Pourquoi cette version?

La version 0.12.0 de huggingface_hub est compatible avec sentence-transformers 2.2.2 car elle contient encore la fonction `cached_download` qui a été supprimée dans les versions ultérieures.

## Comment vérifier que cela fonctionne?

Vous pouvez reconstruire les images Docker et vérifier que le modèle sentence-transformers se charge correctement:

```bash
docker-compose down
docker-compose up -d
```

## Note de compatibilité

Si vous souhaitez mettre à jour `sentence-transformers` vers une version plus récente à l'avenir, assurez-vous de vérifier la compatibilité avec `huggingface_hub` et d'ajuster les versions en conséquence.
