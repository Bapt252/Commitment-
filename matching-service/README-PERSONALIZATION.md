# Guide d'intégration de la personnalisation

Ce document explique comment le service de personnalisation a été intégré au service de matching pour fournir des résultats personnalisés en fonction des préférences utilisateur.

## Architecture

L'architecture d'intégration s'articule autour des composants suivants:

1. **Service de personnalisation** : Service autonome qui gère les préférences utilisateur et personnalise les résultats.
2. **Client de personnalisation** : Composant dans le service de matching qui communique avec le service de personnalisation.
3. **Adaptateur de matching personnalisé** : Couche qui combine les fonctionnalités de base du matching avec la personnalisation.
4. **API de matching étendue** : Points d'entrée qui offrent des options de personnalisation aux clients.

## Fonctionnalités principales

La personnalisation s'applique à deux niveaux principaux:

1. **Personnalisation des poids de matching** : Les différents critères de matching (compétences, expérience, éducation, etc.) reçoivent des poids différents en fonction des préférences de l'utilisateur.
2. **Personnalisation de l'ordre des résultats** : Les résultats sont réordonnés en fonction du comportement passé de l'utilisateur et de ses préférences.

## Flux de travail de personnalisation

1. L'utilisateur effectue une requête de matching ou de recherche.
2. L'API de matching reçoit la requête et vérifie si la personnalisation est demandée.
3. Si la personnalisation est activée, le service de matching appelle le service de personnalisation.
4. Le service de personnalisation ajuste les poids ou réordonne les résultats selon les préférences et le comportement de l'utilisateur.
5. Les résultats personnalisés sont renvoyés à l'utilisateur.
6. Le comportement de l'utilisateur (clics, intérêt, etc.) est enregistré pour améliorer les futures recommandations.

## Comment tester

### Prérequis

- Les services doivent être en cours d'exécution (matching-service, personalization-service, etc.)
- Un token JWT valide pour l'authentification

### Tests automatisés

Un script de test est fourni pour valider l'intégration:

```bash
# Rendre le script exécutable
chmod +x matching-service/test_personalization.sh

# Exécuter les tests
./matching-service/test_personalization.sh
```

Ce script teste:
- La communication entre les services
- Le calcul de matching avec et sans personnalisation
- L'enregistrement des feedbacks
- La mise à jour du statut des matches

### Tests manuels

Pour tester manuellement:

1. Effectuez un calcul de matching sans personnalisation:
   ```bash
   curl -X POST http://localhost:5052/matches/calculate \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{"job_id": 1, "candidate_id": 2, "personalized": false}'
   ```

2. Effectuez le même calcul avec personnalisation:
   ```bash
   curl -X POST http://localhost:5052/matches/calculate \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{"job_id": 1, "candidate_id": 2, "personalized": true}'
   ```

3. Comparez les scores et les classements.

## Comment les données sont collectées

Le système collecte différentes interactions utilisateur:

- **Vue de profil** : Quand un utilisateur consulte un profil candidat ou une offre d'emploi
- **État d'intérêt** : Quand un utilisateur marque son intérêt ou son désintérêt pour un match
- **Clics sur les résultats** : Position des clics dans les listes de résultats
- **Temps passé** : Durée de consultation des profils (si applicable)

Ces données sont utilisées pour:
- Ajuster les poids des critères de matching
- Identifier les similitudes entre utilisateurs (filtrage collaboratif)
- Détecter l'évolution des préférences au fil du temps

## Intégration avec le modèle de données

Les données de personnalisation sont stockées dans Redis pour un accès rapide et dans PostgreSQL pour la persistance à long terme. Les schémas incluent:

- Tables de préférences utilisateur
- Tables de feedback et d'interactions
- Tables de configuration des tests A/B

## Configuration avancée

Le comportement de la personnalisation peut être ajusté via les variables d'environnement:

```
PERSONALIZATION_SERVICE_URL=http://personalization-service:5060
AB_TESTING_ENABLED=true
COLLABORATIVE_FILTER_ENABLED=true
TEMPORAL_DRIFT_ENABLED=true
```

## Dépannage

### Problèmes courants

1. **Préférences non appliquées**: Vérifiez que l'utilisateur a suffisamment d'interactions pour générer des préférences.
2. **Scores identiques**: La personnalisation peut être désactivée ou les préférences peuvent être trop similaires aux poids par défaut.
3. **Erreurs de connexion**: Vérifiez que les services sont en cours d'exécution et accessibles.

### Journalisation

Pour le débogage, activez la journalisation détaillée:

```
LOG_LEVEL=DEBUG
```

Examinez les logs pour voir les appels entre services et les décisions de personnalisation.

## Prochaines étapes

Améliorations potentielles:

1. **Personnalisation plus fine**: Ajouter des sous-catégories de critères de matching
2. **Analyse prédictive**: Anticiper les préférences utilisateur avant leur expression explicite
3. **Interface utilisateur**: Permettre aux utilisateurs de voir et d'ajuster leurs préférences
4. **Tests A/B plus sophistiqués**: Évaluer différentes stratégies de personnalisation

## Conclusion

L'intégration de la personnalisation améliore considérablement la pertinence des résultats de matching en adaptant l'expérience à chaque utilisateur. Avec le temps, à mesure que plus de données d'interaction sont collectées, la qualité des recommandations s'améliore automatiquement.
