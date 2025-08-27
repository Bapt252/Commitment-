# Analyse améliorée de CV avec GPT-4o-mini

Ce document explique comment utiliser le nouveau script d'analyse améliorée de CV qui se concentre sur l'extraction détaillée des expériences professionnelles.

## Fonctionnalités principales

- **Extraction détaillée des expériences professionnelles**
  - Séparation claire entre descriptions, responsabilités et réalisations
  - Identification des technologies utilisées dans chaque poste
  - Détection automatique de la taille d'équipe et du type de contrat

- **Normalisation des dates**
  - Conversion automatique au format YYYY-MM
  - Gestion intelligente des formats variés (français et anglais)
  - Identification des expériences en cours ("Present")

- **Analyse contextuelle**
  - Détection du lieu de travail
  - Identification des projets significatifs
  - Extraction des résultats quantifiables

## Installation et utilisation

### Prérequis

- Python 3.7 ou supérieur
- OpenAI API key
- PyPDF2 (pour l'extraction du texte des PDFs)

### Installation

```bash
# Installer les dépendances nécessaires
pip install openai PyPDF2
```

### Configuration

Définissez votre clé API OpenAI comme variable d'environnement :

```bash
# Sur Linux/Mac
export OPENAI_API_KEY=votre_clé_api_openai

# Sur Windows
set OPENAI_API_KEY=votre_clé_api_openai
```

### Utilisation

Exécutez le script en spécifiant le chemin vers votre CV au format PDF :

```bash
python test_cv_enhanced.py chemin/vers/votre/cv.pdf
```

Par exemple :

```bash
python test_cv_enhanced.py ~/Desktop/MonSuperCV.pdf
```

### Résultats

Le script va :
1. Extraire le texte de votre PDF
2. Analyser le contenu avec GPT-4o-mini et le prompt système amélioré
3. Afficher un résumé des informations extraites
4. Créer un fichier JSON `votrecv_enhanced_parsed.json` avec toutes les données structurées

## Format des données extraites

```json
{
  "nom": "Nom de famille",
  "prenom": "Prénom",
  "poste": "Titre actuel",
  "adresse": "Adresse complète",
  "email": "email@exemple.com",
  "telephone": "+33 6 12 34 56 78",
  "competences": ["JavaScript", "Python", "Docker", ...],
  "logiciels": ["Photoshop", "Excel", "Figma", ...],
  "soft_skills": ["Communication", "Travail d'équipe", ...],
  "experiences": [
    {
      "titre": "Développeur Full Stack",
      "entreprise": "Nom de l'entreprise",
      "lieu": "Paris, France",
      "date_debut": "2022-01",
      "date_fin": "Present",
      "description": "Description générale du poste",
      "responsabilites": [
        "Développement d'applications web",
        "Maintenance de l'infrastructure cloud"
      ],
      "realisations": [
        "Réduction du temps de chargement de 40%",
        "Mise en place d'un CI/CD qui a réduit le temps de déploiement de 30%"
      ],
      "technologies": ["React", "Node.js", "AWS", "Docker"],
      "taille_equipe": 5,
      "type_contrat": "CDI"
    }
  ],
  "formation": [...],
  "certifications": [...]
}
```

## Améliorations par rapport à la version précédente

- Structure plus détaillée des expériences professionnelles
- Meilleure identification des technologies par expérience
- Distinction claire entre responsabilités et réalisations
- Normalisation plus robuste des dates
- Détection du type de contrat et de la taille d'équipe
- Compatibilité avec différentes versions du package OpenAI

## Dépannage

### Erreur "La variable d'environnement OPENAI_API_KEY n'est pas définie"

Assurez-vous d'avoir correctement défini votre clé API OpenAI.

### Erreur lors de l'extraction du texte du PDF

Vérifiez que le fichier est bien au format PDF et qu'il contient du texte extractible (pas un scan d'image).

### Problème de compatibilité OpenAI

Le script est compatible avec les versions 3.x et 4.x du package OpenAI. Si vous rencontrez des erreurs, vérifiez votre version :

```bash
pip show openai
```

## Contribuer

Pour améliorer ce script ou proposer des fonctionnalités supplémentaires, créez une Pull Request sur le dépôt GitHub.
