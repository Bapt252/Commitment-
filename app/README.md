# Module de compatibilité OpenAI

Ce module assure la compatibilité entre les différentes versions de l'API OpenAI et gère spécifiquement les problèmes liés au paramètre `proxies` dans la version 0.28.1.

## Fonctionnalités

- **Suppression du paramètre `proxies`** - Évite les erreurs `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`
- **Conversion des noms de modèles** - Adapte les noms des nouveaux modèles (gpt-4o, gpt-4-turbo, etc.) pour qu'ils fonctionnent avec la version 0.28.1
- **Gestion des timeouts** - Convertit les tuples de timeout en valeurs simples
- **Configuration de l'API key** - Détecte automatiquement la clé API à partir des variables d'environnement
- **Compatibilité bidirectionnelle** - Fonctionne avec d'anciennes versions d'OpenAI et avec les récentes

## Utilisation

### 1. Importer en premier dans vos scripts

Il est crucial d'importer ce module avant toute autre importation d'OpenAI :

```python
# Importer le patch de compatibilité OpenAI en premier
import app.compat

# Reste des imports...
import openai
# etc...
```

### 2. Utiliser l'API OpenAI normalement

Le patch s'applique automatiquement, vous pouvez utiliser l'API normalement :

```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Vous êtes un assistant utile."},
        {"role": "user", "content": "Bonjour!"}
    ],
    proxies={"http": "http://proxy:8080"}  # Ce paramètre sera automatiquement supprimé
)
```

### 3. Log et débogage

Le module utilise le logging Python standard pour signaler les opérations effectuées. Vous pouvez voir les détails dans les logs.

## Développement

Si vous avez besoin d'étendre les fonctionnalités de compatibilité :

1. Ajoutez des conversions de modèles dans le dictionnaire `model_mapping`
2. Ajoutez des traitements pour d'autres paramètres incompatibles
3. Étendez la fonction `patch_openai()` pour gérer d'autres cas spécifiques

## Note importante

Ce module est une solution temporaire pour maintenir la compatibilité avec OpenAI 0.28.1. À terme, il est recommandé de migrer vers la nouvelle API OpenAI lorsque votre projet sera prêt.
