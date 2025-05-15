# Intégration de l'Analyseur Sémantique avec Nexten SmartMatch

Ce document décrit comment l'analyseur sémantique de compétences est intégré au système de matching bidirectionnel Nexten SmartMatch.

## Vue d'ensemble

L'analyseur sémantique permet une comparaison plus intelligente des compétences entre les candidats et les offres d'emploi, allant au-delà de la simple correspondance de mots-clés. Il comprend:

- **Reconnaissance des compétences liées** : identification des technologies et frameworks connexes (ex: React et JavaScript)
- **Analyse de similarité textuelle** : détection des variations de formulation (ex: ReactJS et React.js)
- **Support de WordNet** (optionnel) : utilisation de ressources linguistiques pour identifier les synonymes

## Tests simplifiés

En raison de la complexité des dépendances dans la structure du projet, nous avons ajouté un script de test indépendant qui peut être exécuté sans problèmes d'importation :

```bash
# Rendre le script exécutable
chmod +x run-isolated-semantic-tests.sh

# Exécuter les tests isolés
./run-isolated-semantic-tests.sh
```

Ce script exécute les tests unitaires dans un environnement isolé, ce qui permet de vérifier le bon fonctionnement de l'analyseur sémantique sans dépendre de la structure complète du projet.

## Intégration dans le système

L'analyseur sémantique est conçu pour être intégré au moteur de matching existant, particulièrement dans la version améliorée `EnhancedMatchingEngine`.

### Modification du fichier `matching_engine_enhanced.py`

Pour intégrer l'analyseur sémantique, modifiez le fichier `matching_engine_enhanced.py` en ajoutant:

```python
# Ajouter l'import en haut du fichier
from app.semantic.analyzer import SemanticAnalyzer

class EnhancedMatchingEngine:
    def __init__(self):
        # Ajouter cette ligne aux initialisations existantes
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Reste des initialisations...
        self.cv_data = {}
        self.questionnaire_data = {}
        self.job_data = {}
        self.preferences = {}
    
    # Modifier la méthode de calcul des scores de compétences
    def _calculate_skills_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des compétences en utilisant l'analyseur sémantique
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Extraire les compétences du CV et du job
        cv_skills = [skill.lower() for skill in self.cv_data.get('competences', [])]
        job_skills = [skill.lower() for skill in job.get('competences', [])]
        
        # Si pas de compétences listées, retourner un score par défaut
        if not job_skills:
            return 0.5
        
        # Utiliser l'analyseur sémantique pour calculer la similarité
        return self.semantic_analyzer.calculate_skills_similarity(cv_skills, job_skills)
```

## Comportement de l'analyseur sémantique

### Fonctionnement du calcul de similarité

L'analyseur sémantique utilise une approche en plusieurs étapes :

1. **Correspondance directe** : Vérification des compétences exactement identiques
   - Si toutes les compétences du poste sont dans le CV, le score est 1.0 (correspondance parfaite)
   
2. **Correspondance sémantique** : Pour les compétences qui ne correspondent pas exactement
   - Utilisation d'un dictionnaire de relations entre compétences
   - Analyse de similarité textuelle pour les variations orthographiques
   - Analyse via WordNet pour les synonymes (si disponible)

3. **Calcul du score combiné** :
   - En cas de correspondance partielle, la formule est : `(direct_match_score * 0.7) + (semantic_match_score * 0.3)`
   - Cette pondération donne plus d'importance aux correspondances directes

## Performances et optimisations

L'analyseur sémantique utilise plusieurs niveaux d'analyse, avec des optimisations pour équilibrer précision et performance:

1. **Premier niveau** : Correspondance directe (rapide)
2. **Deuxième niveau** : Vérification des compétences liées via dictionnaire (rapide)
3. **Troisième niveau** : Analyse de similarité textuelle (modérée)
4. **Quatrième niveau** : Analyse WordNet si disponible (plus lente)

Cette approche en cascade assure que les méthodes les plus coûteuses ne sont utilisées qu'en dernier recours.

## Améliorations futures

Voici quelques pistes d'amélioration pour l'analyseur sémantique:

- **Apprentissage automatique** : Entraîner un modèle sur des données réelles de CV et offres
- **Enrichissement du dictionnaire** : Ajouter plus de relations entre compétences
- **Extraction contextuelle** : Prendre en compte le contexte d'utilisation des compétences
- **Analyse multilingue** : Support de l'analyse sémantique dans différentes langues
