# Guide d'Intégration de SmartMatch avec les Services de Parsing Existants

Ce guide explique comment intégrer et utiliser le système SmartMatch avec les services de parsing de CV et de fiches de poste existants.

## Architecture

Le système SmartMatch utilise une architecture adaptateur/interface pour s'intégrer avec les services de parsing existants :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CV Parser     │    │  Job Parser     │    │  Other Parsers  │
│   Service       │    │  Service        │    │  (future)       │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌──────────────────────────────────────────────────────────────┐
│             Adapters (ExistingCVParserAdapter,               │
│             ExistingJobParserAdapter, etc.)                  │
└────────────────────────────┬───────────────────────────────┬─┘
                             │                               │
                             ▼                               │
┌────────────────────────────────────────────┐              │
│          CombinedParserService             │              │
└────────────────────────┬───────────────────┘              │
                         │                                   │
                         ▼                                   ▼
┌─────────────────────────────────────┐      ┌─────────────────────────┐
│          ParsingAdapter             │◄─────┤    MatchingPipeline     │
└─────────────────┬───────────────────┘      └─────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│          SmartMatcher               │
└─────────────────────────────────────┘
```

## Configuration

1. **Fichier .env** : Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```
CV_PARSER_URL=http://localhost:5051
JOB_PARSER_URL=http://localhost:5055
DEFAULT_PARSER_SERVICE=combined
MATCHING_RESULTS_DIR=matching_results
```

2. **Variables d'environnement** :
   - `CV_PARSER_URL` : URL du service de parsing de CV
   - `JOB_PARSER_URL` : URL du service de parsing de fiches de poste
   - `DEFAULT_PARSER_SERVICE` : Type de service de parsing à utiliser (combined, cv, job)
   - `MATCHING_RESULTS_DIR` : Répertoire pour stocker les résultats

## Utilisation

### En ligne de commande

```bash
# Démarrer le serveur avec les paramètres par défaut
python run_matching_api.py

# Démarrer le serveur avec des paramètres personnalisés
python run_matching_api.py --host 0.0.0.0 --port 5052 --cv-parser-url http://localhost:5051 --job-parser-url http://localhost:5055 --parser-service combined
```

### Options disponibles

```
--host TEXT                 Adresse d'hôte (défaut: 0.0.0.0)
--port INTEGER              Port d'écoute (défaut: 5052)
--debug                     Activer le mode debug
--cv-parser-url TEXT        URL du service de parsing de CV (défaut: http://localhost:5051)
--job-parser-url TEXT       URL du service de parsing de fiches de poste (défaut: http://localhost:5055)
--results-dir TEXT          Répertoire pour stocker les résultats (défaut: matching_results)
--parser-service TEXT       Type de service de parsing à utiliser (combined, cv, job) (défaut: combined)
```

### API REST

Une fois le serveur démarré, vous pouvez utiliser l'API REST :

#### Health Check

```
GET /health
```

#### Matching direct

```
POST /match/direct
Content-Type: application/json

{
  "cv_data": {...},
  "job_data": {...}
}
```

#### Matching CV vers Job

```
POST /match/cv-to-job
Content-Type: multipart/form-data

cv_file: <fichier CV>
job_description: <description du poste en texte>
```

#### Matching Job vers CV

```
POST /match/job-to-cv
Content-Type: multipart/form-data

job_description: <description du poste en texte>
cv_file: <fichier CV>
```

#### Matching fichier de poste vers CV

```
POST /match/job-file-to-cv
Content-Type: multipart/form-data

job_file: <fichier de poste>
cv_file: <fichier CV>
```

## Intégration avec Votre Code

### Créer un ServiceFactory

```python
from app.factories import ServiceFactory

# Créer un service de parsing
parser_service = ServiceFactory.create_parser_service(
    service_type="combined",
    cv_parser_url="http://localhost:5051",
    job_parser_url="http://localhost:5055"
)

# Créer un adaptateur de parsing
parsing_adapter = ServiceFactory.create_parsing_adapter(parser_service)

# Créer un pipeline de matching
from app.adapters.matching_pipeline import MatchingPipeline
pipeline = MatchingPipeline(parsing_adapter)
```

### Utiliser le Pipeline de Matching

```python
# Matcher un CV et une fiche de poste
with open("path/to/cv.pdf", "rb") as cv_file:
    cv_content = cv_file.read()

job_description = "Description du poste..."

result = await pipeline.match_cv_to_job(cv_content, "cv.pdf", job_description)
print(f"Score de matching: {result['score']}")
print(f"Détails: {result['details']}")
```

## Extension et Personnalisation

### Ajouter un Nouveau Service de Parsing

1. Créez une nouvelle classe implémentant l'interface `ParserServiceInterface` :

```python
from app.services.parser_service_interface import ParserServiceInterface

class MyCustomParserService(ParserServiceInterface):
    def __init__(self, api_url=None):
        self.api_url = api_url
    
    async def parse_cv(self, file_content, file_name=None):
        # Votre implémentation
        pass
    
    async def parse_job(self, job_description):
        # Votre implémentation
        pass
```

2. Ajoutez le nouveau service à la factory :

```python
# Mettre à jour app/factories/service_factory.py
@staticmethod
def create_parser_service(service_type="combined", cv_parser_url=None, job_parser_url=None):
    if service_type.lower() == "combined":
        return CombinedParserService(cv_parser_url, job_parser_url)
    elif service_type.lower() == "cv":
        return ExistingCVParserAdapter(cv_parser_url)
    elif service_type.lower() == "job":
        return ExistingJobParserAdapter(job_parser_url)
    elif service_type.lower() == "custom":
        return MyCustomParserService(cv_parser_url)
    else:
        raise ValueError(f"Type de service de parsing non reconnu: {service_type}")
```

## Diagnostic et Dépannage

### Problèmes d'API

Si vous rencontrez des problèmes avec les services de parsing, vérifiez :

1. Que les services sont en cours d'exécution et accessibles
2. Que les URLs sont correctement configurées
3. Les logs du serveur pour les erreurs détaillées

### Logging

Le système utilise le module `logging` de Python. Vous pouvez ajuster le niveau de log :

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Ou INFO, WARNING, ERROR, etc.
```

### Mode Fallback

En cas d'erreur lors du parsing, le système utilise un mode de fallback qui simule le parsing avec des données de base. Cela permet de continuer à fonctionner même si les services de parsing sont temporairement indisponibles.
