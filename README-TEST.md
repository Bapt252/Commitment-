# Guide de test du Parser CV

Ce guide explique comment tester le système de parsing CV "Commitment-" dans ses deux modes : mock (simulation) et réel (avec OpenAI).

## Prérequis

- Docker et docker-compose installés
- Le système "Commitment-" correctement configuré
- Une clé API OpenAI valide (pour le mode réel)

## Configuration de la clé API OpenAI

Pour utiliser le parser CV en mode réel, vous devez configurer la clé API OpenAI. Deux options s'offrent à vous :

### Option 1 : Utiliser la clé depuis GitHub Secrets

Si vous avez configuré la clé API OpenAI dans les secrets GitHub, utilisez le script suivant :

```bash
# Exporter la clé API depuis GitHub Secrets
export OPENAI_API_KEY=votre_clé_api_ici

# Démarrer le service avec la clé API
./start-parser-with-api-key.sh
```

### Option 2 : Configurer manuellement le fichier .env

Vous pouvez également modifier directement le fichier `cv-parser-service/.env` :

```bash
# Éditer le fichier .env
nano cv-parser-service/.env

# Modifier ces lignes :
USE_MOCK_PARSER=false
OPENAI_API_KEY=votre_clé_api_ici

# Redémarrer le service
docker-compose restart nexten-cv-parser
```

## Scripts de test disponibles

### 1. Test du parser réel

Pour tester si le parser utilise correctement l'API OpenAI :

```bash
./test-real-parser.sh
```

Ce script envoie un CV exemple au service et affiche le résultat parsé.

### 2. Comparaison des parsers (mock vs réel)

Pour comparer les résultats entre le mock parser et le parser réel :

```bash
# Utiliser un CV exemple généré automatiquement
./compare-parsers.sh

# Ou spécifier votre propre fichier CV
./compare-parsers.sh votre_cv.pdf
```

Ce script vous permet de voir la différence entre les données générées aléatoirement (mock) et les véritables données extraites par OpenAI.

### 3. Redémarrage en mode réel

Pour redémarrer rapidement le service en mode réel :

```bash
./restart-cv-parser-real.sh
```

## Différences entre mock et parser réel

| Mock Parser | Parser Réel (OpenAI) |
|-------------|----------------------|
| Génère des données aléatoires | Extrait les données réelles du CV |
| Toujours disponible, même hors ligne | Nécessite une connexion internet et une clé API valide |
| Gratuit, pas de coût d'API | Consomme des crédits OpenAI |
| Structure de données simplifiée | Structure de données plus riche et détaillée |

## Personnalisation de l'extraction

Pour personnaliser l'extraction des CV, vous pouvez modifier les fichiers suivants :

1. `cv-parser-service/app/services/parser.py` - Contient le prompt utilisé pour l'extraction avec OpenAI (fonction `analyze_cv_with_gpt`)

2. `cv-parser-service/app/core/config.py` - Contient les paramètres de configuration comme le modèle OpenAI à utiliser

3. `cv-parser-service/app/services/resilience.py` - Contient la logique d'appel à l'API OpenAI avec gestion des erreurs

## Exemples de personnalisation

### Modifier le prompt d'extraction

Pour modifier les informations extraites ou leur format, éditez la variable `prompt` dans la fonction `analyze_cv_with_gpt` du fichier `cv-parser-service/app/services/parser.py` :

```python
prompt = f"""
Tu es un assistant spécialisé dans l'extraction d'informations à partir de CV.
Extrait les informations suivantes du CV ci-dessous et retourne-les dans un format JSON structuré.

# Personnalisez ici les catégories et instructions d'extraction selon vos besoins

CV:
{cv_text}

Retourne uniquement un objet JSON sans introduction ni commentaire.
"""
```

### Changer le modèle OpenAI

Pour utiliser un modèle différent, modifiez le fichier `cv-parser-service/.env` :

```
# Modèle OpenAI à utiliser (exemples : gpt-4o-mini, gpt-4, gpt-3.5-turbo)
OPENAI_MODEL=gpt-4
```

## Dépannage

### Le parser utilise toujours le mode mock

1. Vérifiez que `USE_MOCK_PARSER=false` dans le fichier `cv-parser-service/.env`
2. Vérifiez que `OPENAI_API_KEY` est correctement défini
3. Redémarrez le service avec `docker-compose restart nexten-cv-parser`

### Erreurs d'API OpenAI

Si vous rencontrez des erreurs avec l'API OpenAI :

1. Vérifiez que votre clé API est valide et possède des crédits
2. Consultez les logs du conteneur : `docker logs nexten-cv-parser`
3. En cas d'erreur de rate limit, attendez quelques minutes avant de réessayer

## Support

Pour toute question ou problème, veuillez contacter l'équipe de développement ou ouvrir une issue sur GitHub.
