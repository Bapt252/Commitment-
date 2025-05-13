# API d'analyse GPT pour fiches de poste

Ce service fournit une API REST pour l'analyse des fiches de poste en utilisant GPT. Il permet d'extraire automatiquement les informations pertinentes des fiches de poste, comme le titre, l'entreprise, la localisation, les compétences requises, etc.

## Prérequis

- Python 3.8 ou supérieur
- Flask
- PyPDF2
- OpenAI API (clé API requise)

## Installation

1. Assurez-vous que Python est installé sur votre système.
2. Installez les dépendances requises :

```bash
pip install flask flask-cors openai pypdf2
```

3. Définissez votre clé API OpenAI en tant que variable d'environnement :

```bash
export OPENAI_API_KEY="votre-clé-api-openai"
```

## Démarrage du service

```bash
python gpt_parser_api.py
```

Le service démarrera sur le port 5055 par défaut. Vous pouvez accéder à l'API à l'adresse `http://localhost:5055`.

## Endpoints API

### Vérification de l'état

```
GET /health
```

Renvoie l'état de santé de l'API.

### Analyse par texte

```
POST /analyze
```

Corps de la requête (JSON) :
```json
{
  "text": "Texte de la fiche de poste..."
}
```

### Analyse par fichier

```
POST /analyze-file
```

Corps de la requête (multipart/form-data) :
- `file` : Fichier de la fiche de poste (formats acceptés : PDF, DOCX, DOC, TXT, max 5 Mo)

## Exemple de réponse

```json
{
  "status": "success",
  "job_info": {
    "title": "Développeur Full Stack JavaScript",
    "company": "TechInnovate",
    "location": "Paris, France",
    "contract_type": "CDI",
    "skills": ["JavaScript", "React", "Node.js", "TypeScript", "Git"],
    "experience": "3-5 ans",
    "education": "Bac+5 en informatique ou équivalent",
    "salary": "45K€ - 60K€ selon expérience",
    "responsibilities": [
      "Développer des applications web modernes",
      "Participer à la conception des architectures"
    ],
    "benefits": [
      "Télétravail 3 jours par semaine",
      "RTT",
      "Mutuelle d'entreprise"
    ]
  },
  "metadata": {
    "analyzed_at": "2025-05-13T12:34:56.789Z",
    "parser_version": "1.0.0-gpt"
  }
}
```

## Intégration avec l'interface web

Pour intégrer cette API avec l'interface web existante, mettez à jour le fichier `scripts/gpt-analyze.js` en désactivant le mode de simulation et en configurant les bonnes URL API.

## Déploiement avec Docker

Un fichier Dockerfile est inclus pour faciliter le déploiement. Pour créer et démarrer le conteneur Docker :

```bash
docker build -t job-parser-gpt-api .
docker run -p 5055:5055 -e OPENAI_API_KEY="votre-clé-api-openai" job-parser-gpt-api
```

## Dépannage

Si vous rencontrez des problèmes avec l'API, vérifiez les points suivants :

1. Assurez-vous que la clé API OpenAI est correctement définie.
2. Vérifiez que les dépendances sont installées.
3. Consultez les logs pour plus d'informations sur les erreurs.
