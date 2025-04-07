# Système de parsing amélioré pour Commitment

Ce dossier contient le système de parsing amélioré permettant d'extraire des informations structureées à partir de différents types de documents (CV, offres d'emploi, etc.) avec des capacités avancées d'analyse.

## Fonctionnalités principales

- **Détection automatique du format** : Analyse automatique du type de fichier et extraction du texte adaptée à chaque format (PDF, DOCX, TXT, HTML, etc.)
- **Extraction d'informations implicites** : Utilisation de BERT pour déduire des informations non explicites dans les documents
- **Déduction des préférences d'environnement et de travail** : Analyse des CV pour détecter les préférences des candidats (télétravail, startup, travail en équipe, etc.)
- **Système de feedback et d'amélioration continue** : Collecte des corrections des utilisateurs pour améliorer automatiquement les extractions futures

## Architecture du système

Le système de parsing amélioré est composé de quatre composants principaux:

1. **Parseur adaptatif** (`adaptive_parser.py`) :
   - Détection automatique du format et type de document
   - Extraction du texte adaptée au format détecté
   - Prétraitement du document selon son type

2. **NLP avancé** (`advanced_nlp.py`) :
   - Utilisation de BERT pour l'extraction d'informations implicites
   - Reconnaissance d'entités nommées, analyse de sentiment
   - Extraction d'informations par question-réponse

3. **Extracteur de préférences** (`environment_preference_extractor.py`) :
   - Déduction des préférences d'environnement (télétravail, startup, etc.)
   - Détection des styles de travail préférés (autonomie, travail d'équipe, etc.)

4. **Système de feedback** (`parser_feedback_system.py`) :
   - Collecte des corrections effectuées par les utilisateurs
   - Constitution d'un dataset d'entraînement
   - Application automatique des corrections similaires

5. **Système d'intégration** (`enhanced_parsing_system.py`) :
   - Coordonne tous les composants pour une expérience unifiée
   - Interface simple pour l'utilisation du système complet

## Utilisation du système

### Parsing simple d'un document

```python
from app.nlp.enhanced_parsing_system import parse_document

# Parsing depuis un fichier
result = parse_document(file_path="chemin/vers/document.pdf")

# Parsing depuis un contenu texte
result = parse_document(text_content="Texte du document", doc_type="cv")

# Accès aux données extraites
extracted_data = result["extracted_data"]
confidence_scores = result["confidence_scores"]

# Accès aux préférences déduites (pour les CV)
if "preferences" in extracted_data:
    environment_prefs = extracted_data["preferences"]["environment"]
    work_style_prefs = extracted_data["preferences"]["work_style"]
```

### Enregistrement des feedbacks utilisateurs

```python
from app.nlp.enhanced_parsing_system import save_parsing_feedback

# Enregistrer une correction faite par un utilisateur
feedback_id = save_parsing_feedback(
    original_result=result_original,    # Résultat avant correction
    corrected_result=result_corrige,    # Résultat après correction
    user_id="identifiant_utilisateur"   # Optionnel
)
```

### Export des données d'entraînement

```python
from app.nlp.enhanced_parsing_system import export_training_dataset

# Exporter toutes les données d'entraînement
success = export_training_dataset("chemin/vers/dossier_export")

# Exporter seulement les données d'un type spécifique
success = export_training_dataset("chemin/vers/dossier_export", doc_type="cv")
```

## Configuration requise

Le système de parsing amélioré nécessite les dépendances suivantes:

- Python 3.9+
- Les bibliothèques listées dans `requirements.txt`
- Pour les capacités BERT complètes: GPU recommandé avec CUDA

## Extensions et personnalisation

### Ajout de nouveaux types de documents

Pour ajouter un nouveau type de document à parser:

1. Créer un nouveau module `nouveau_type_parser.py`
2. Implémenter une fonction `extract_nouveau_type_data(text: str) -> Dict[str, Any]`
3. Mettre à jour `enhanced_parsing_system.py` pour inclure le nouveau type

### Personnalisation des modèles BERT

Les modèles BERT peuvent être fine-tunés avec les données collectées par le système de feedback:

1. Exporter les données d'entraînement avec `export_training_dataset()`
2. Utiliser les scripts dans le dossier `ml_engine` pour le fine-tuning
3. Remplacer ou mettre à jour les modèles dans le dossier approprié

## Exemple complet d'utilisation

Consultez `example_usage.py` pour un exemple complet montrant comment:

- Détecter automatiquement le format et le type de document
- Extraire des informations complètes avec BERT
- Déduire les préférences d'environnement et de travail
- Collecter et utiliser les feedbacks des utilisateurs