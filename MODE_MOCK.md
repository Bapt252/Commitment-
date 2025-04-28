# Mode Mock pour le Service de Parsing CV

Ce document explique les modifications apportées au service de parsing CV pour permettre le fonctionnement même sans accès à l'API OpenAI.

## Résumé des modifications

1. **Ajout d'un service de mock parsing**
   - Nouveau fichier: `cv-parser-service/app/services/mock_parser.py`
   - Ce service simule l'analyse de CV en générant des données structurées fictives mais réalistes

2. **Modification de la configuration**
   - Ajout du paramètre `USE_MOCK_PARSER` (activé par défaut)
   - Changement du modèle par défaut de `gpt-4o-mini` à `gpt-3.5-turbo` (plus largement disponible)

3. **Modification du service de parsing**
   - Ajout d'un mécanisme de fallback automatique vers le mock en cas d'erreur OpenAI
   - Intégration transparente du mock parser avec l'API existante

4. **Ajout de scripts de test**
   - `test-direct-api.sh`: Pour tester l'API directe de parsing
   - `test-mock-parser.sh`: Pour tester spécifiquement le mode mock
   - `parse_cv_direct_test.sh`: Script amélioré avec meilleure gestion des erreurs

## Comment utiliser le mode mock

### Configuration

Le mode mock est activé par défaut dans la configuration. Pour le désactiver, vous pouvez:

1. Modifier le fichier `.env`:
   ```
   USE_MOCK_PARSER=false
   ```

2. Ou utiliser une variable d'environnement:
   ```bash
   export USE_MOCK_PARSER=false
   ```

### Test avec le script

Pour tester le parsing en mode mock:

```bash
# Rendre le script exécutable
chmod +x test-mock-parser.sh

# Exécuter le script
./test-mock-parser.sh
```

Ce script enverra votre CV au service et utilisera le mock parser pour l'analyser, même en l'absence de connexion à l'API OpenAI.

## Fonctionnement technique

Le service de mock parsing utilise les informations suivantes pour générer des données simulées:

1. **Nom du fichier CV**: Le nom du fichier est analysé pour extraire un nom et prénom potentiels
2. **Données aléatoires**: Des compétences, expériences, formations et autres informations sont sélectionnées aléatoirement à partir de listes prédéfinies
3. **Structure cohérente**: Les données générées suivent la même structure que celles produites par l'API OpenAI

## Format des données générées

Les données générées par le mock parser comprennent:

- Informations personnelles (nom, email, téléphone, etc.)
- Compétences techniques et logiciels
- Expériences professionnelles
- Formation
- Langues
- Certifications
- Intérêts

## Avantages du mode mock

1. **Développement et tests sans API OpenAI**: Permet de développer et tester l'application sans consommer de crédits API
2. **Résilience**: L'application continue de fonctionner même en cas de problème d'API
3. **Démonstrations**: Facilite les démos de l'application sans dépendre d'une connexion internet ou d'un service externe

## Limitations

1. **Données fictives**: Les données générées ne reflètent pas le contenu réel du CV
2. **Variété limitée**: Les données sont sélectionnées parmi un ensemble prédéfini d'éléments
