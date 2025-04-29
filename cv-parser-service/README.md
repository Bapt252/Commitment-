
# Service de Parsing CV

Ce service utilise GPT-4o-mini pour extraire des informations structurées à partir de CV.

## Fonctionnalités

- Extraction de texte à partir de plusieurs formats de CV (PDF, DOCX, DOC, TXT, RTF)
- Analyse du texte avec GPT-4o-mini pour extraire les informations structurées
- API REST pour le parsing direct ou asynchrone via des files d'attente Redis
- Stockage des résultats dans Redis et/ou MinIO
- OCR pour les PDF numérisés (lorsque les bibliothèques nécessaires sont installées)

## Configuration

Créez un fichier `.env` à la racine du projet avec les paramètres suivants :

```env
# Obligatoire: Clé API OpenAI
OPENAI=your_openai_api_key_here

# Paramètres optionnels 
OPENAI_MODEL=gpt-4o-mini  # Modèle recommandé
USE_MOCK_PARSER=false     # Ne pas utiliser le mock
LOG_LEVEL=INFO            # Niveau de logging (DEBUG pour plus d'informations)
```

## Dépannage du parsing CV

Si vous rencontrez des problèmes de parsing avec certains CV, voici quelques solutions :

### 1. Problèmes d'extraction de texte

Le parsing peut échouer si le texte n'est pas correctement extrait du CV :

- **PDF scannés**: Utilisez l'OCR (active par défaut si les dépendances sont présentes) 
- **PDF protégés**: Essayez de supprimer la protection du PDF ou convertissez-le en un autre format
- **Formats exotiques**: Convertissez le CV en PDF standard ou DOCX avant de l'uploader

### 2. Problèmes de parsing OpenAI

Si l'extraction de texte fonctionne mais l'analyse échoue :

- Vérifiez que votre clé API OpenAI est valide et active
- Activez le mode debug pour voir la réponse brute d'OpenAI
- Essayez un autre modèle OpenAI (gpt-4o-mini, gpt-3.5-turbo, etc.)

### 3. Problèmes de structure ou langue

- Le système fonctionne mieux avec des CV en français ou anglais
- Les CV très atypiques ou avec des mises en page complexes peuvent poser problème

## Commandes utiles

```bash
# Reconstruire et redémarrer le service avec mode debug
./rebuild-cv-parser.sh

# Voir les logs en temps réel 
docker-compose logs -f cv-parser

# Tester le service directement avec curl
curl -X POST -F "file=@/chemin/vers/votre/cv.pdf" http://localhost:5051/api/parse-cv
```

## Notes sur la compatibilité des CV

Le système a été testé et optimisé pour les formats suivants :

- PDF standards (non scannés)
- DOCX modernes
- Documents texte simples

Pour une meilleure compatibilité, évitez :
- Les PDF avec des filigranes ou sécurisés  
- Les formats propriétaires ou obsolètes
- Les documents excessivement formatés

En cas de problème persistant, convertissez votre CV en PDF simple ou DOCX avant l'upload.
