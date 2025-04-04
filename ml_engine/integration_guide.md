# Guide d'intégration du moteur ML pour Commitment

Ce guide explique comment intégrer le moteur de Machine Learning dans l'application frontend existante.

## Prérequis

- Python 3.8+ installé
- pip (gestionnaire de paquets Python)
- Accès au serveur où l'API ML sera déployée

## Installation et configuration

1. **Cloner le dépôt du projet**

```bash
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-
git checkout feature/ml-integration
```

2. **Installer les dépendances Python**

```bash
cd ml_engine
pip install -r requirements.txt
```

3. **Configurer l'environnement**

```bash
python setup.py
```

4. **Initialiser la base de données avec des exemples**

```bash
python train_models.py --setup-sample
```

5. **Entraîner les modèles initiaux**

```bash
python train_models.py
```

## Démarrage du serveur API

```bash
python api.py
```

Le serveur API sera accessible à l'adresse http://localhost:8000

## Intégration avec le frontend

Il existe deux méthodes pour intégrer le moteur ML au frontend existant.

### Méthode 1: Intégration transparente (recommandée)

Ajoutez simplement le script `frontend_integration.js` à votre page HTML avant le script `job-description-parser.js` :

```html
<!-- Intégration ML (ajouter avant job-description-parser.js) -->
<script src="/ml_engine/frontend_integration.js"></script>

<!-- Script existant -->
<script src="/static/scripts/job-description-parser.js"></script>
```

Cette méthode a l'avantage de remplacer automatiquement la fonction `parseJobDescription` par une version qui utilise l'API ML, tout en conservant le comportement original comme fallback si l'API n'est pas disponible.

### Méthode 2: Modification du code original

Si vous préférez modifier directement le code original, vous pouvez remplacer la fonction `parseJobDescription` dans `job-description-parser.js` par une version asynchrone qui appelle l'API ML:

```javascript
// Remplacer cette fonction
async function parseJobDescription(jobDescription) {
  try {
    // Appeler l'API ML
    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: jobDescription }),
    });

    if (!response.ok) {
      // Fallback vers l'analyse basée sur des règles
      return parseJobDescriptionRuleBased(jobDescription);
    }

    const mlResult = await response.json();
    
    // Convertir le format de l'API ML au format attendu par le frontend
    return {
      jobTitle: mlResult.job_title || '',
      experience: mlResult.experience || '',
      skills: mlResult.skills || [],
      education: mlResult.education || '',
      contract: mlResult.contract || '',
      location: mlResult.location || '',
      salary: mlResult.salary || '',
      rawText: jobDescription,
      confidence: mlResult.confidence_scores || {}
    };
    
  } catch (error) {
    console.warn('Erreur lors de l\'utilisation de l\'API ML, repli sur le système basé sur des règles.');
    return parseJobDescriptionRuleBased(jobDescription);
  }
}
```

N'oubliez pas de sauvegarder la fonction originale sous le nom `parseJobDescriptionRuleBased` au début du fichier.

## Système de feedback

Pour permettre à l'IA de s'améliorer grâce aux corrections des utilisateurs, nous avons ajouté un système de feedback. À chaque fois qu'un utilisateur modifie les résultats de l'analyse et applique ces modifications, un feedback est envoyé à l'API ML.

Ce système est déjà configuré dans la méthode d'intégration transparente. Si vous utilisez la méthode 2, vous devrez ajouter des gestionnaires d'événements pour capturer les modifications et les envoyer via `sendMLFeedback`.

## Déploiement en production

Pour un déploiement en production :

1. Installez le module ML sur un serveur accessible depuis votre frontend
2. Configurez un serveur WSGI (comme Gunicorn) pour l'API
3. Utilisez un proxy inverse (comme Nginx) pour servir l'API
4. Modifiez les URLs dans `frontend_integration.js` pour pointer vers l'URL de production
5. Sécurisez l'API avec une authentification appropriée

```bash
# Exemple de démarrage avec Gunicorn
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Maintenance et amélioration continue

Pour améliorer continuellement les modèles :

1. Collectez régulièrement les feedbacks des utilisateurs
2. Réentraînez les modèles avec les nouvelles données annotées
3. Déployez les nouveaux modèles

```bash
# Réentraînement périodique
python train_models.py --limit 5000  # Utiliser plus de données au fur et à mesure
```