# Job Parser CLI

Un outil en ligne de commande pour extraire automatiquement les informations des fiches de poste au format PDF.

## Fonctionnalités

- Extraction du texte de fichiers PDF
- Détection automatique des informations clés :
  - Titre du poste
  - Entreprise
  - Localisation
  - Type de contrat (CDI, CDD, etc.)
  - Compétences requises
  - Expérience demandée
  - Formation/Éducation
  - Salaire
  - Description du poste
  - Date de publication
- Sauvegarde des résultats au format JSON
- Interface en ligne de commande simple

## Prérequis

- Python 3.6 ou supérieur
- Bibliothèque PyPDF2 (pour l'extraction de texte des PDFs)

## Installation

Assurez-vous d'avoir les dépendances requises :

```bash
pip install PyPDF2
```

## Utilisation

### Commande de base

```bash
python job_parser_cli.py /chemin/vers/fiche_de_poste.pdf
```

### Options disponibles

- `--output` ou `-o` : Spécifier un chemin personnalisé pour le fichier de sortie JSON
- `--verbose` ou `-v` : Activer le mode verbeux pour plus d'informations de débogage

### Exemples

Analyser une fiche de poste et utiliser le nom de fichier par défaut pour la sortie :
```bash
python job_parser_cli.py ~/Desktop/fdp.pdf
```

Analyser une fiche de poste et spécifier un nom de fichier pour la sortie :
```bash
python job_parser_cli.py ~/Desktop/fdp.pdf -o resultats_parsing.json
```

Activer le mode verbeux pour le débogage :
```bash
python job_parser_cli.py ~/Desktop/fdp.pdf -v
```

## Sortie

Le script génère un fichier JSON contenant toutes les informations extraites, avec la structure suivante :

```json
{
  "parsing_metadata": {
    "pdf_path": "/chemin/vers/fiche_de_poste.pdf",
    "filename": "fiche_de_poste.pdf",
    "parsed_at": "2025-05-12T11:51:15.123456",
    "parser_version": "1.0.0"
  },
  "job_info": {
    "titre_poste": "Développeur Full-Stack",
    "entreprise": "Exemple Entreprise",
    "localisation": "Paris, France",
    "type_contrat": "CDI",
    "competences": ["JavaScript", "React", "Node.js", "Python", "MongoDB"],
    "experience": "3 ans minimum",
    "formation": "Bac+5 en informatique",
    "salaire": "45-55K€",
    "description": "Description détaillée du poste...",
    "date_publication": "2025-05-01"
  }
}
```

## Personnalisation

Le script utilise des expressions régulières pour extraire les informations. Vous pouvez les personnaliser en modifiant les patterns dans la fonction `extract_job_info()` pour les adapter à vos besoins spécifiques.

## Dépannage

Si le script ne détecte pas correctement les informations :

1. Utilisez l'option `-v` pour activer le mode verbeux et voir le texte brut extrait du PDF
2. Vérifiez que le PDF contient du texte sélectionnable (et non des images de texte)
3. Ajustez les expressions régulières dans le code si nécessaire pour correspondre au format de vos fiches de poste

## Limitations

- Le script fonctionne mieux avec des PDFs contenant du texte sélectionnable
- Les PDFs scannés ou les images nécessitent une OCR préalable (non incluse)
- La précision de l'extraction dépend de la structure et du format de la fiche de poste
