# Parsing CV Amélioré avec GPT-4o-mini

Cette fonctionnalité améliore l'extraction d'informations à partir des CV, en mettant particulièrement l'accent sur les expériences professionnelles et leur structuration détaillée.

## Nouvelles fonctionnalités

- **Extraction détaillée des expériences professionnelles** : Séparation claire entre descriptions, responsabilités et réalisations
- **Détection des technologies par expérience** : Identification des technologies utilisées dans chaque poste
- **Normalisation des dates** : Conversion automatique vers le format YYYY-MM
- **Extraction contextuelle** : Détection de la taille d'équipe et du type de contrat
- **Approche en deux passes** : Raffinement spécifique des expériences après extraction initiale

## Comment utiliser la fonctionnalité

### 1. Utilisation via le script de test

Un script de test est fourni pour tester rapidement le parsing amélioré sur n'importe quel CV :

```bash
# Depuis le répertoire cv-parser-service
python test_enhanced_parser.py chemin/vers/MonSuperCV.pdf
```

Options disponibles :
- `-v, --verbose` : Active le mode verbeux avec plus de détails
- `-f, --force` : Force le rafraîchissement du cache Redis
- `-r, --raw` : Affiche le JSON brut au lieu du format formaté

### 2. Intégration dans l'API existante

Les améliorations sont déjà intégrées dans le service principal. Utilisez l'API comme d'habitude :

```bash
curl -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/votre/cv.pdf" \
  -F "force_refresh=false"
```

## Format de sortie JSON amélioré

```json
{
  "nom": "Doe",
  "prenom": "John",
  "poste": "Développeur Full-Stack Senior",
  "adresse": "123 Rue de l'Innovation, Paris, France",
  "email": "john.doe@example.com",
  "telephone": "+33 6 12 34 56 78",
  "competences": ["JavaScript", "React", "Node.js", "Python", "Docker"],
  "logiciels": ["Git", "VS Code", "Jira", "Figma"],
  "soft_skills": ["Communication", "Travail d'équipe", "Leadership"],
  "experiences": [
    {
      "titre": "Développeur Full-Stack Senior",
      "entreprise": "TechCorp",
      "lieu": "Paris",
      "date_debut": "2021-01",
      "date_fin": "Present",
      "description": "Responsable du développement d'une plateforme e-commerce générant 2M€ de revenus annuels",
      "responsabilites": [
        "Développement et maintenance d'une plateforme e-commerce",
        "Implémentation d'une architecture microservices avec Node.js",
        "Direction d'une équipe de 4 développeurs junior"
      ],
      "realisations": [
        "Réduction des temps de déploiement de 40%",
        "Augmentation de la performance du site de 60%"
      ],
      "technologies": ["React", "Node.js", "MongoDB", "AWS", "Docker"],
      "taille_equipe": 4,
      "type_contrat": "CDI"
    }
  ],
  "formation": [
    {
      "diplome": "Master en Informatique",
      "etablissement": "Université de Paris",
      "lieu": "Paris",
      "date_debut": "2018-09",
      "date_fin": "2020-06",
      "description": "Spécialisation en développement web et mobile",
      "distinctions": ["Mention Très Bien", "Major de promotion"]
    }
  ],
  "certifications": [
    {
      "nom": "AWS Certified Developer",
      "organisme": "Amazon Web Services",
      "date_obtention": "2022-03",
      "date_expiration": "2025-03"
    }
  ]
}
```

## Prompt système optimisé

Le prompt système a été optimisé pour :

1. Extraire plus d'informations contextuelles des expériences
2. Séparer clairement les responsabilités des réalisations concrètes
3. Identifier les technologies utilisées dans chaque poste
4. Normaliser les formats de date
5. Détecter automatiquement le type de contrat et la taille d'équipe

## Fonctionnement technique

### Extraction en deux passes

1. **Première passe** : Extraction globale des informations du CV
2. **Seconde passe** : Raffinement spécifique des expériences professionnelles

### Normalisation des dates

Le système normalise automatiquement les dates au format ISO YYYY-MM, en gérant :
- Différents formats (JJ/MM/AAAA, MM-AAAA, etc.)
- Mois écrits en toutes lettres (français et anglais)
- Dates partielles (année seule)
- Expériences en cours ("Présent", "Actuel", etc.)

### Extraction contextuelle

L'extraction contextuelle analyse le texte pour détecter :
- Type de contrat (CDI, CDD, Freelance, Stage)
- Taille d'équipe (nombre de personnes supervisées)
- Lieu précis (ville, pays)

## Dépannage

### Le script de test ne fonctionne pas

```bash
# Vérifier que vous avez les dépendances nécessaires
pip install openai redis tenacity PyPDF2 python-docx

# S'assurer que votre clé API OpenAI est configurée
export OPENAI_API_KEY=votre_clé_api
```

### Erreurs de parsing

Si vous rencontrez des erreurs lors du parsing, vérifiez :

1. Que le CV est bien lisible (texte extractible, pas un scan d'image)
2. Que la clé API OpenAI est valide
3. Les logs pour plus de détails sur l'erreur

## Développement futur

- Extraction plus précise des compétences techniques par niveau de maîtrise
- Analyse de correspondance entre CV et offres d'emploi
- Interface utilisateur pour visualiser et modifier les résultats du parsing
- Validation automatique des informations extraites

## Contribuer

Les contributions sont les bienvenues ! Pour proposer des améliorations :

1. Créez une branche à partir de `feature/enhanced-cv-parsing`
2. Apportez vos modifications
3. Soumettez une pull request avec une description détaillée
