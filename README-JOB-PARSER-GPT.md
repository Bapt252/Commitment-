# Fonctionnalité d'analyse de fiches de poste avec GPT

Cette fonctionnalité permet d'analyser automatiquement les fiches de poste à l'aide de GPT et d'extraire les informations structurées.

## Composants

1. **Backend API**: Un endpoint FastAPI qui traite les fichiers PDF, DOCX et TXT pour en extraire le texte et l'analyser avec GPT.
2. **Frontend JavaScript**: Un client JavaScript qui communique avec l'API et un script d'intégration qui ajoute un bouton "Analyser avec GPT" à l'interface.

## Installation

### Backend

Le backend utilise FastAPI et expose un endpoint `/api/parse-with-gpt` qui accepte un fichier en entrée et renvoie les informations extraites au format JSON.

Le routeur est défini dans le fichier `backend/app/routes/gpt_parser.py` et est intégré à l'application principale dans `backend/app/api/api.py`.

### Frontend

Deux fichiers JavaScript sont fournis:
- `js/gpt-parser-client.js`: Classe client pour communiquer avec l'API
- `js/gpt-integration.js`: Script pour intégrer le bouton "Analyser avec GPT" à l'interface utilisateur

Pour inclure ces scripts dans votre page HTML, ajoutez ces lignes avant la fermeture de la balise `</body>`:

```html
<script src="../js/gpt-parser-client.js"></script>
<script src="../js/gpt-integration.js"></script>
```

## Utilisation

1. Téléchargez une fiche de poste (PDF, DOCX ou TXT) via l'interface
2. Cliquez sur le bouton "Analyser avec GPT" 
3. Les informations extraites seront affichées et les champs du formulaire seront automatiquement remplis

## Structure des données

L'API renvoie un objet JSON avec la structure suivante:

```json
{
  "success": true,
  "data": {
    "titre_poste": "Titre du poste",
    "entreprise": "Nom de l'entreprise",
    "localisation": "Lieu de travail",
    "type_contrat": "Type de contrat",
    "competences": ["Compétence 1", "Compétence 2", "..."],
    "experience": "Expérience requise",
    "formation": "Formation requise",
    "salaire": "Salaire proposé",
    "description": "Description du poste"
  },
  "processing_time": "0.85 secondes"
}
```

## Dépannage

1. **Problème**: Le bouton "Analyser avec GPT" n'apparaît pas
   **Solution**: Vérifiez que les scripts sont correctement inclus et que les éléments DOM nécessaires (zone de dépôt, input file) existent dans votre page.

2. **Problème**: Erreur 500 lors de l'analyse
   **Solution**: Vérifiez que le script parse_fdp_gpt.py est accessible par le backend et que la clé API OpenAI est correctement configurée dans le fichier .env.

3. **Problème**: Résultats d'analyse vides ou incorrects
   **Solution**: Vérifiez que le format de la fiche de poste est correct et que le texte peut être extrait correctement. Le mode debug peut aider à diagnostiquer les problèmes.

## API Reference

### Endpoint: `/api/parse-with-gpt`

**Méthode**: POST

**Corps de la requête**: FormData avec un champ `file` contenant le fichier à analyser

**Réponse**: 
- `200 OK`: L'analyse a réussi, renvoie les données extraites
- `400 Bad Request`: Format de fichier non supporté
- `500 Internal Server Error`: Erreur lors du traitement ou de l'analyse

## Notes de développement

Cette fonctionnalité s'appuie sur le script `parse_fdp_gpt.py` qui doit être accessible dans le PYTHONPATH du backend. Le script utilise l'API OpenAI pour l'analyse, assurez-vous qu'une clé API valide est configurée.
