# Guide de test du système de parsing CV

Ce guide explique comment tester le système de parsing CV, avec les options pour utiliser le vrai parser au lieu du mode mock.

## 1. Configuration du service

Par défaut, le service de parsing CV fonctionne en mode "mock" (simulation), ce qui signifie qu'il génère des données de test plutôt que d'analyser réellement les CV. Pour utiliser le vrai parser, vous devez modifier la configuration et redémarrer le service.

### Option 1 : Redémarrer avec le mode réel

```bash
# Téléchargez les dernières modifications
git pull

# Rendez le script exécutable
chmod +x restart-cv-parser-real.sh

# Exécutez le script de redémarrage
./restart-cv-parser-real.sh
```

Ce script :
1. Crée ou modifie le fichier `.env` dans `cv-parser-service/` pour définir `USE_MOCK_PARSER=false`
2. Redémarre les conteneurs Docker nécessaires
3. Vérifie que le service est correctement démarré

### Option 2 : Modifier manuellement le fichier .env

Si vous préférez le faire manuellement :

1. Créez ou modifiez le fichier `cv-parser-service/.env` :
   ```
   USE_MOCK_PARSER=false
   ```

2. Redémarrez les services :
   ```bash
   docker-compose stop cv-parser cv-parser-worker
   docker-compose up -d cv-parser cv-parser-worker
   ```

## 2. Tester le service

### Option 1 : Utiliser le script de test

```bash
# Téléchargez les dernières modifications
git pull

# Rendez le script exécutable
chmod +x test-real-parser.sh

# Testez avec votre CV
./test-real-parser.sh ~/Desktop/MonSuperCV.pdf
```

Ce script :
1. Vérifie que le service est accessible
2. Envoie votre CV au service en mode "force_refresh" pour éviter le cache
3. Vérifie si le service utilise le mode mock ou réel
4. Sauvegarde et affiche les résultats

### Option 2 : Utiliser les scripts existants

```bash
# Pour un test simple
./parse_cv_simple.sh --refresh ~/Desktop/MonSuperCV.pdf

# Pour un test direct
./parse_cv_direct.sh ~/Desktop/MonSuperCV.pdf
```

### Option 3 : Utiliser l'API directement

```bash
curl -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@~/Desktop/MonSuperCV.pdf" \
  -F "force_refresh=true"
```

## 3. Vérifier les résultats

Les résultats sont enregistrés dans des fichiers JSON :
- `real_parser_result.json` : Résultats du test avec le parser réel
- `result_final.json` : Résultats du test avec `parse_cv_simple.sh`
- `direct_parsing_result.json` : Résultats du test avec `parse_cv_direct.sh`

Pour vérifier si le mode mock est toujours actif, cherchez la valeur `"model": "mock"` dans le résultat JSON. Si vous utilisez le vrai parser, il affichera plutôt le modèle utilisé (par exemple, `"model": "gpt-3.5-turbo"`).

## Notes importantes

1. **Clé API OpenAI** : Si vous utilisez le vrai parser (non-mock), vous aurez besoin d'une clé API OpenAI valide. Modifiez le fichier `.env` pour inclure votre clé :
   ```
   OPENAI=votre_clé_api_openai_ici
   ```

2. **Configuration avancée** : Pour des configurations plus avancées, vous pouvez modifier d'autres paramètres dans le fichier `.env`, comme le modèle OpenAI utilisé :
   ```
   OPENAI_MODEL=gpt-3.5-turbo
   ```

3. **Dépannage** : Si le service ne fonctionne pas comme prévu :
   - Vérifiez les logs : `docker logs nexten-cv-parser`
   - Assurez-vous que les conteneurs sont en cours d'exécution : `docker-compose ps`
   - Vérifiez que le fichier `.env` est correctement configuré
