# Job Parser avec GPT

Ce dossier contient le backend pour le parser de fiches de poste utilisant GPT.

## Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Installer les dépendances :

```bash
pip install flask flask-cors requests PyPDF2 python-docx
```

2. Configurer la clé API OpenAI :

```bash
# Sur Linux/Mac
export OPENAI_API_KEY=votre_clé_api_openai

# Sur Windows (PowerShell)
$env:OPENAI_API_KEY = "votre_clé_api_openai"

# Sur Windows (CMD)
set OPENAI_API_KEY=votre_clé_api_openai
```

## Exécution

Pour démarrer le serveur backend :

```bash
python job_parser_api.py
```

Par défaut, le serveur écoutera sur le port 5055.

## Configuration avancée

Vous pouvez configurer les paramètres suivants via des variables d'environnement :

- `PORT` : Port d'écoute du serveur (défaut : 5055)
- `OPENAI_API_KEY` : Clé API OpenAI
- `DEBUG` : Mode debug (True/False)

## API Endpoints

### Analyser une fiche de poste

**Endpoint** : `/api/parse-job`
**Méthode** : `POST`
**Format** : `multipart/form-data`

**Paramètres** :
- `file` : Fichier de la fiche de poste (PDF, DOCX, TXT)
  OU
- `text` : Texte brut de la fiche de poste

**Réponse** :
```json
{
  "title": "Titre du poste",
  "company": "Nom de l'entreprise",
  "location": "Localisation",
  "contract_type": "Type de contrat",
  "skills": ["Compétence 1", "Compétence 2"],
  "experience": "Expérience requise",
  "education": "Formation requise",
  "salary": "Salaire proposé",
  "responsibilities": ["Responsabilité 1", "Responsabilité 2"],
  "benefits": ["Avantage 1", "Avantage 2"]
}
```

### Vérifier l'état du serveur

**Endpoint** : `/api/health`
**Méthode** : `GET`

**Réponse** :
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## Intégration avec le frontend

Le frontend est déjà configuré pour se connecter à ce backend. Par défaut, il utilise l'URL `http://localhost:5055/api/parse-job`.

Vous pouvez modifier cette URL en passant le paramètre `apiUrl` dans l'URL du frontend :

```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?apiUrl=http://votre-serveur:5055
```
