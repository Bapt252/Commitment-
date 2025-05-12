# Correctif pour l'Erreur de Journalisation du Job Parser

Ce document explique comment résoudre l'erreur liée à la configuration de journalisation dans le service job-parser.

## Problème

Après avoir résolu l'erreur d'indentation dans le fichier `config.py`, une nouvelle erreur est apparue lors du démarrage du service :

```
AttributeError: 'Settings' object has no attribute 'LOG_DIR'
```

Cette erreur indique que les paramètres de journalisation sont manquants dans la classe `Settings` du fichier `config.py`.

## Solution

Nous avons apporté plusieurs correctifs pour résoudre ce problème :

1. **Ajout des paramètres de journalisation manquants** : Nous avons ajouté les paramètres suivants à la classe `Settings` dans le fichier `config.py` :
   - `LOG_DIR` : Répertoire où les fichiers de logs seront stockés
   - `LOG_LEVEL` : Niveau de journalisation (INFO, DEBUG, etc.)
   - `LOG_FORMAT` : Format des logs (text ou json)

2. **Script de correction de configuration** : Un nouveau script `fix-logging-config.sh` a été ajouté pour ajouter automatiquement ces paramètres dans le conteneur Docker.

3. **Mise à jour du script entrypoint.sh** : Le script d'entrée a été modifié pour créer le répertoire de logs et exécuter le script de correction de configuration.

4. **Script de reconstruction** : Un nouveau script `fix-job-parser-logging.sh` a été ajouté pour faciliter la reconstruction et le redémarrage du service avec les corrections.

## Comment utiliser la solution

Pour résoudre le problème, exécutez simplement le script de reconstruction suivant :

```bash
# Télécharger le script depuis GitHub
curl -o fix-job-parser-logging.sh https://raw.githubusercontent.com/Bapt252/Commitment-/main/fix-job-parser-logging.sh

# Rendre le script exécutable
chmod +x fix-job-parser-logging.sh

# Exécuter le script
./fix-job-parser-logging.sh
```

Ce script va :
1. Mettre à jour votre dépôt local avec les dernières modifications
2. Arrêter le service job-parser existant
3. Reconstruire l'image Docker avec nos corrections
4. Redémarrer le service
5. Vérifier que tout fonctionne correctement

## Vérification

Après avoir appliqué les correctifs, vérifiez que le service démarre correctement en consultant les logs :

```bash
docker-compose logs job-parser
```

Vous devriez voir un démarrage normal sans aucune erreur liée à la journalisation.

## Paramètres de journalisation ajoutés

Les paramètres suivants ont été ajoutés à la configuration :

```python
# Configuration de journalisation
LOG_DIR: str = os.environ.get('LOG_DIR') or 'logs'
LOG_LEVEL: str = os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FORMAT: str = os.environ.get('LOG_FORMAT') or 'text'  # 'text' ou 'json'
```

Ces paramètres peuvent être personnalisés à l'aide de variables d'environnement si nécessaire.
