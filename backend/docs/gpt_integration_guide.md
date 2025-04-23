# Guide d'intégration de l'API GPT pour le système de parsing

Ce guide détaille l'intégration de l'API GPT (OpenAI) dans le système de parsing de la plateforme Commitment.

## Aperçu

L'intégration de l'API GPT apporte les avantages suivants :

- Extraction plus précise des informations depuis les CV, offres d'emploi et questionnaires
- Meilleure compréhension du contexte et des nuances dans les textes
- Meilleure détection des compétences implicites et des préférences de travail
- Amélioration continue des résultats grâce au système de feedback

## Installation

1. Mettez à jour les dépendances :

```bash
pip install -r requirements.txt
```

2. Configurez votre clé API dans le fichier `.env` :

```
OPENAI_API_KEY=your_openai_api_key
GPT_MODEL=gpt-4  # Options: gpt-3.5-turbo, gpt-4, gpt-4-turbo
```

## Utilisation

### Utilisation par défaut

Le système de parsing utilisera automatiquement GPT si une clé API valide est détectée dans l'environnement. Aucune modification n'est nécessaire dans vos appels existants :

```python
from app.nlp.enhanced_parsing_system import parse_document

# Le système utilisera GPT si la clé API est disponible
result = parse_document(file_path="chemin/vers/document.pdf", doc_type="cv")
```

### Contrôle explicite du parsing GPT

Vous pouvez également contrôler explicitement si GPT doit être utilisé pour un document spécifique :

```python
# Forcer l'utilisation de GPT pour un document
result_with_gpt = parse_document(
    text_content=text,
    doc_type="job_posting",
    use_gpt=True  # Forcer l'utilisation de GPT
)

# Désactiver l'utilisation de GPT
result_without_gpt = parse_document(
    file_path="chemin/vers/document.pdf",
    doc_type="company_questionnaire",
    use_gpt=False  # Forcer l'utilisation des méthodes traditionnelles
)
```

### Gestion des métriques et du suivi

Le système indique la méthode de parsing utilisée dans les résultats :

```python
# Vérifier la méthode utilisée
method = result.get("parsing_method")  # "gpt" ou "traditional"
preference_method = result.get("preference_extraction_method")  # "gpt" ou "traditional"

# Log pour le suivi
logging.info(f"Document traité avec méthode: {method}")
```

## Recommandations d'utilisation

### Optimisation des coûts

L'utilisation de l'API OpenAI génère des coûts basés sur le nombre de tokens. Pour optimiser les coûts :

1. Utiliser GPT prioritairement pour les documents complexes ou importants
2. Limiter la taille des documents en pré-filtrant les sections non pertinentes
3. Considérer l'utilisation de modèles moins coûteux comme `gpt-3.5-turbo` pour les documents standard

### Fallback automatique

Le système inclut un mécanisme de fallback automatique : si GPT échoue pour une raison quelconque, le système utilisera automatiquement les méthodes traditionnelles de parsing. Cela garantit que le système reste fonctionnel même en cas de problème avec l'API OpenAI.

## Personnalisation des prompts

Les prompts utilisés pour interroger GPT sont définis dans le fichier `gpt_parser.py`. Vous pouvez les personnaliser pour améliorer les résultats selon vos besoins spécifiques :

1. Ouvrez `backend/app/nlp/gpt_parser.py`
2. Localisez les méthodes qui créent les prompts (comme `_create_cv_prompt`, `_create_job_prompt`, etc.)
3. Modifiez les instructions données à GPT pour améliorer la qualité ou la structure des extractions

## Suivi et maintenance

Surveillez régulièrement :

1. Les taux de succès des extractions GPT vs traditionnelles
2. Les coûts API associés à l'utilisation de GPT
3. Les feedbacks utilisateurs pour ajuster les prompts et améliorer la qualité des extractions

## Dépannage

### Problèmes courants et solutions

- **Erreur de clé API** : Assurez-vous que la clé API est correctement définie dans le fichier `.env`
- **Erreur de quota dépassé** : Vérifiez votre utilisation et limites sur le tableau de bord OpenAI
- **Résultats incohérents** : Ajustez les prompts pour obtenir des structures plus cohérentes
- **Texte tronqué** : Si les documents sont trop grands, envisagez de les diviser en sections avant le traitement

### Logs

Le système enregistre des informations détaillées dans les logs pour faciliter le dépannage. Vérifiez les logs pour identifier les problèmes potentiels :

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Exemples d'utilisation avancée

### Intégration dans une API FastAPI

```python
from fastapi import FastAPI, UploadFile, File, Query
from app.nlp.enhanced_parsing_system import parse_document

app = FastAPI()

@app.post("/api/parse-document")
async def parse_document_api(
    file: UploadFile = File(...),
    doc_type: str = Query(None),
    use_gpt: bool = Query(True)
):
    content = await file.read()
    result = parse_document(
        file_content=content,
        file_name=file.filename,
        doc_type=doc_type,
        use_gpt=use_gpt
    )
    return result
```

### Traitement par lots

```python
import os
from app.nlp.enhanced_parsing_system import parse_document

def process_directory(directory_path, doc_type=None, use_gpt=True):
    results = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                result = parse_document(file_path=file_path, doc_type=doc_type, use_gpt=use_gpt)
                results.append({"filename": filename, "result": result})
            except Exception as e:
                results.append({"filename": filename, "error": str(e)})
    return results
```
