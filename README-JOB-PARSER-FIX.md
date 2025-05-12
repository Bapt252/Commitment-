# Corrections pour le service job-parser

Ce patch corrige les problèmes de compatibilité entre Pydantic v1 et v2 dans le service de parsing de fiches de poste, ainsi que les erreurs de syntaxe dans le script `entrypoint.sh`.

## Problèmes corrigés

1. **Erreur de syntaxe** - Résout l'erreur `unexpected EOF while looking for matching '"'` dans le script entrypoint.sh
2. **Compatibilité Pydantic** - Corrige l'erreur `BaseSettings has been moved to the pydantic-settings package`
3. **Scripts utilitaires** - Ajoute des scripts pour faciliter la gestion et les tests

## Comment appliquer les corrections

### Méthode 1 : Utiliser le script de correction rapide (pour déploiements existants)

```bash
# Télécharger le script
curl -o fix-job-parser.sh https://raw.githubusercontent.com/Bapt252/Commitment-/fix-job-parser-clean/fix-job-parser.sh

# Rendre le script exécutable
chmod +x fix-job-parser.sh

# Exécuter le script
./fix-job-parser.sh
```

### Méthode 2 : Mettre à jour et reconstruire manuellement

1. **Mettre à jour le code source** :
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Rendre les scripts exécutables** :
   ```bash
   chmod +x restart-job-parser.sh curl-test-job-parser.sh
   ```

3. **Redémarrer le service** :
   ```bash
   ./restart-job-parser.sh
   ```

## Scripts utilitaires inclus

1. **restart-job-parser.sh** - Pour redémarrer rapidement le service :
   ```bash
   ./restart-job-parser.sh
   ```

2. **curl-test-job-parser.sh** - Pour tester le parsing d'une fiche de poste :
   ```bash
   ./curl-test-job-parser.sh ~/Desktop/fichedeposte.pdf
   ```

3. **fix-job-parser.sh** - Pour corriger rapidement un déploiement existant :
   ```bash
   ./fix-job-parser.sh
   ```

## Configuration OpenAI

Assurez-vous que votre fichier `.env` contient une clé API OpenAI valide :

```
OPENAI=votre_clé_api_openai_réelle
```

Si aucune clé n'est fournie, le service passera automatiquement en mode simulation (mock).

## Problèmes connus

Si le service ne démarre toujours pas après ces corrections, essayez :

1. **Reconstruire entièrement les images** :
   ```bash
   docker-compose down
   docker-compose build --no-cache job-parser job-parser-worker
   docker-compose up -d
   ```

2. **Vérifier les logs** :
   ```bash
   docker-compose logs -f job-parser
   ```

## Support

Si vous rencontrez d'autres problèmes, veuillez ouvrir une issue sur le dépôt GitHub.