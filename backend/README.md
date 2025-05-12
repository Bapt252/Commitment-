# Backend Commitment

Backend pour le projet Commitment, incluant l'analyse de CV et de fiches de poste avec GPT.

## Nouvelles fonctionnalités

### Job Parser avec GPT

Le service d'analyse de fiches de poste a été ajouté ! Il permet d'extraire automatiquement les informations clés des fiches de poste à l'aide de GPT.

#### Configuration

1. Assurez-vous d'avoir une clé API OpenAI valide
2. Copiez le fichier `.env.example` vers `.env` et configurez votre clé API :
   ```
   cp .env.example .env
   ```
3. Modifiez le fichier `.env` pour ajouter votre clé API OpenAI :
   ```
   OPENAI_API_KEY=sk-votre-clé-api
   ```

#### Installation des dépendances

```bash
pip install -r requirements.txt
```

#### Démarrage du service

```bash
python run.py
```

#### Utilisation de l'API Job Parser

Le service expose plusieurs endpoints :

- `POST /api/job-parser/queue` : Soumettre un job d'analyse (fichier PDF ou texte)
- `GET /api/job-parser/result/<job_id>` : Récupérer le résultat d'un job
- `GET /api/job-parser/health` : Vérifier l'état du service

Exemple d'utilisation avec cURL :

```bash
# Soumettre un fichier PDF
curl -X POST -F "file=@fiche_de_poste.pdf" http://localhost:5000/api/job-parser/queue

# Soumettre du texte
curl -X POST -F "text=Développeur Web Senior. Entreprise: TechCorp. Expérience: 5+ ans." http://localhost:5000/api/job-parser/queue

# Récupérer le résultat
curl http://localhost:5000/api/job-parser/result/12345-uuid-67890
```

## Architecture

Le backend est organisé comme suit :

- `app/` : Application principale
  - `routes/` : Définition des routes de l'API
  - `models/` : Modèles de données
  - `services/` : Services métier
- `job_parser_service.py` : Service d'analyse des fiches de poste
- `parsing_service.py` : Service d'analyse des CV
- `app.py` : Point d'entrée de l'application
- `run.py` : Script de démarrage

## Intégration avec le frontend

Le frontend peut se connecter au backend via l'API. Pour activer le mode debug, ajoutez `?debug=true` à l'URL du frontend.

## Troubleshooting

Si vous rencontrez des problèmes, vérifiez les points suivants :

1. La clé API OpenAI est correctement configurée
2. Les dépendances sont correctement installées
3. Le port 5000 est disponible
4. Les logs dans la console pour identifier les erreurs

## Développement

Pour les développeurs, voici quelques commandes utiles :

```bash
# Lancer les tests
pytest

# Vérifier la qualité du code
flake8

# Formater le code
black .
```
