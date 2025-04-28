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
   - Séparation des installations en étapes distinctes pour éviter les problèmes de dépendances
   - Ajout de commandes pour vérifier les versions installées

## Pourquoi cette version?

La version 0.12.0 de huggingface_hub est compatible avec sentence-transformers 2.2.2 car elle contient encore la fonction `cached_download` qui a été supprimée dans les versions ultérieures.

## Comment résoudre le problème

Pour s'assurer que le problème est complètement résolu, nous avons créé un script `rebuild-all.sh` qui effectue un nettoyage complet et une reconstruction des containers Docker sans utiliser le cache.

Suivez ces étapes pour résoudre le problème:

1. Rendez le script exécutable:
   ```bash
   chmod +x rebuild-all.sh
   ```

2. Exécutez le script:
   ```bash
   ./rebuild-all.sh
   ```

Ce script va:
- Arrêter tous les containers Docker
- Supprimer les images Docker liées au projet
- Nettoyer le cache Docker
- Reconstruire tous les services sans utiliser le cache
- Démarrer tous les containers

## Vérification des versions installées

Si vous souhaitez vérifier manuellement les versions de packages installées dans un container, vous pouvez exécuter:

```bash
docker exec nexten-api pip freeze | grep huggingface
docker exec nexten-api pip freeze | grep sentence
```

Vous devriez voir:
- huggingface_hub==0.12.0
- sentence-transformers==2.2.2

## Note de compatibilité

Si vous souhaitez mettre à jour `sentence-transformers` vers une version plus récente à l'avenir, assurez-vous de vérifier la compatibilité avec `huggingface_hub` et d'ajuster les versions en conséquence.

Les versions compatibles sont:
- sentence-transformers 2.2.2 avec huggingface_hub 0.12.0 (solution actuelle)
- sentence-transformers 2.2.2 avec huggingface_hub <= 0.14.1
- sentence-transformers >= 2.3.0 avec huggingface_hub >= 0.16.0

Si vous rencontrez toujours des problèmes après un rebuild complet, vérifiez que les volumes Docker ne contiennent pas d'anciens fichiers qui pourraient interférer avec l'installation.
