# Modification du Job Parser Service pour utiliser GPT

Ce document détaille les modifications apportées au service de parsing de fiches de poste (`job-parser-service`) pour adopter la même structure que le service de parsing de CV (`cv-parser-service`), notamment pour l'utilisation des modèles GPT.

## Modifications réalisées

1. **Ajout d'une configuration cohérente** 
   - Création d'un fichier `config.py` à la racine du service
   - Mise à jour du fichier de configuration dans `app/core/config.py`

2. **Implémentation d'un système de mock parser**
   - Ajout d'un fichier `mock_parser.py` dans `app/services/`
   - Génération de données fictives mais réalistes pour les tests et le développement

3. **Amélioration de l'extraction de texte**
   - Implémentation de méthodes robustes pour différents formats de fichiers (PDF, DOCX, DOC, TXT, RTF)
   - Gestion des erreurs et mécanismes de fallback

4. **Ajout d'un service de résilience**
   - Création d'un fichier `resilience.py` dans `app/services/`
   - Implémentation d'un circuit breaker et d'un mécanisme de retry pour les appels à l'API OpenAI

5. **Préchargement des modèles et dépendances**
   - Ajout d'un fichier `preload_models.py` pour accélérer le démarrage du service

6. **Amélioration du parser principal**
   - Mise à jour du fichier `parser.py` dans `app/services/` pour utiliser la même structure que le cv-parser-service
   - Ajout de fonctions de pré-traitement et post-traitement plus avancées

7. **Mise à jour du point d'entrée principal**
   - Modification du fichier `main.py` pour être cohérent avec la nouvelle structure

## Utilisation

Le service de parsing de fiches de poste fonctionne maintenant de la même manière que le service de parsing de CV. Il peut être utilisé de deux façons :

1. **Avec l'API OpenAI (mode normal)** 
   - Nécessite une clé API OpenAI valide dans le fichier `.env` ou les variables d'environnement
   - Utilise le modèle GPT spécifié dans la configuration (par défaut : `gpt-4o-mini`)

2. **Sans API OpenAI (mode mock)** 
   - Activé automatiquement si aucune clé API n'est fournie
   - Peut être activé explicitement avec la variable d'environnement `USE_MOCK_PARSER=true`
   - Génère des données fictives mais réalistes pour les tests et le développement

## Améliorations par rapport à la version précédente

- **Robustesse** : Meilleure gestion des erreurs à tous les niveaux
- **Résilience** : Circuit breaker et mécanisme de retry pour les appels à l'API
- **Extraction de texte** : Support de plus de formats avec des méthodes de fallback
- **Données de test** : Génération de données fictives réalistes pour le développement
- **Configuration** : Structure de configuration plus claire et cohérente
- **Performance** : Préchargement des modèles et dépendances au démarrage

## Structure du service

```
job-parser-service/
├── app/
│   ├── api/
│   ├── core/
│   │   └── config.py          # Configuration spécifique à l'app
│   ├── services/
│   │   ├── mock_parser.py     # Générateur de données fictives
│   │   ├── parser.py          # Parser principal
│   │   └── resilience.py      # Circuit breaker et retry
│   ├── utils/
│   └── workers/
├── config.py                  # Configuration globale
├── main.py                    # Point d'entrée principal
├── preload_models.py          # Préchargement des modèles
└── requirements.txt           # Dépendances
```

## Exemple d'utilisation via l'API

```bash
# Test de l'endpoint health
curl http://localhost:5053/health

# Parsing d'une fiche de poste
curl -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/fiche_poste.pdf" \
  -F "force_refresh=false"
```

## Remarques

- Le service utilise désormais le même modèle GPT que le service de parsing de CV
- Les deux services partagent une structure similaire pour faciliter la maintenance
- Les données extraites sont adaptées aux fiches de poste (titre, entreprise, compétences requises, etc.)
