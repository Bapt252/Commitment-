# Guide d'intégration du JOB PARSER avec le frontend

Ce guide explique comment connecter le service JOB PARSER backend avec le frontend existant pour permettre l'extraction automatique d'informations à partir de fiches de poste.

## Prérequis

- Node.js 14+ et npm installés
- Docker et Docker Compose installés (pour exécuter le service backend)
- Le projet Commitment cloné et fonctionnel

## 1. Installation des fichiers d'intégration

### 1.1 Installer la bibliothèque d'API JOB PARSER

Créez un nouveau fichier `job-parser-api.js` dans le dossier `js` du projet :

```bash
mkdir -p js
cp job-parser-api.js js/
```

### 1.2 Ajouter la page d'intégration (optionnel)

Si vous souhaitez tester l'intégration séparément, copiez le fichier d'exemple :

```bash
cp job-parser-integration.html templates/
```

### 1.3 Configurer le proxy

Pour éviter les problèmes de CORS entre le frontend et le backend, installez et configurez le proxy :

```bash
npm install express http-proxy-middleware cors
cp proxy-job-parser.js ./
```

## 2. Configuration du service JOB PARSER

### 2.1 Démarrer le service JOB PARSER

Utilisez le script de démarrage du JOB PARSER fourni dans le projet :

```bash
./restart-job-parser.sh
```

Ou utilisez Docker Compose directement :

```bash
docker-compose up -d job-parser-service
```

### 2.2 Vérifier que le service est fonctionnel

Testez que le service répond correctement :

```bash
curl http://localhost:5053/health
```

Vous devriez obtenir une réponse indiquant que le service est en cours d'exécution.

## 3. Intégration avec client-questionnaire.html

### 3.1 Ajouter les références aux scripts dans client-questionnaire.html

Ouvrez `templates/client-questionnaire.html` et ajoutez les références aux scripts après la ligne qui inclut le parser.js existant :

```html
<!-- Scripts -->
<script src="../assets/js/parser.js"></script>
<script src="../js/job-parser-api.js"></script>
```

### 3.2 Modifier le code d'analyse de la fiche de poste

Dans le fichier `templates/client-questionnaire.html`, nous avons déjà:

1. Importé le script `job-parser-api.js`
2. Initialisé l'API JOB PARSER dans le code JavaScript
3. Modifié la fonction qui gère l'analyse des fichiers
4. Modifié la fonction qui gère l'analyse du texte de la fiche de poste
5. Ajouté un fallback sur l'analyseur local si l'API backend n'est pas disponible

## 4. Lancement du proxy et test

### 4.1 Démarrer le serveur proxy

```bash
node proxy-job-parser.js
```

### 4.2 Accéder à l'interface

Ouvrez votre navigateur et accédez à :

```
http://localhost:8080/templates/client-questionnaire.html
```

Vous pouvez également tester l'exemple d'intégration directement :

```
http://localhost:8080/templates/job-parser-integration.html
```

## 5. Résolution des problèmes courants

### Problèmes de CORS

Si vous rencontrez des erreurs CORS dans la console du navigateur, assurez-vous que :

1. Le proxy est correctement configuré et en cours d'exécution
2. L'URL de l'API dans `job-parser-api.js` est correcte
3. Le service JOB PARSER a le header CORS `Access-Control-Allow-Origin` configuré

### Service JOB PARSER inaccessible

Si le service JOB PARSER n'est pas accessible, vérifiez que :

1. Le conteneur Docker est en cours d'exécution : `docker ps | grep job-parser`
2. Le port est correctement exposé : `docker-compose ps job-parser-service`
3. Vous pouvez accéder directement au service : `curl http://localhost:5053/health`

### Erreurs d'analyse

Si l'analyse échoue mais que le service est fonctionnel :

1. Vérifiez les logs du service : `docker logs commitment-job-parser-service`
2. Assurez-vous que le format du fichier est pris en charge (PDF, DOCX, TXT)
3. Vérifiez que le contenu du fichier ou du texte est bien une fiche de poste

## 6. Configuration avancée

### Mode Mock pour le développement

Pour utiliser le mode mock du service JOB PARSER pendant le développement, ajoutez la variable d'environnement `USE_MOCK_PARSER=true` :

```bash
USE_MOCK_PARSER=true docker-compose up -d job-parser-service
```

### Déploiement en production

Pour un déploiement en production, modifiez les configurations suivantes :

1. Changez l'URL de l'API dans `job-parser-api.js` pour utiliser l'URL de production
2. Configurez CORS pour n'autoriser que les domaines de production
3. Utilisez un serveur web comme Nginx ou Apache pour le proxy au lieu du script Node.js

---

Pour toute question supplémentaire, consultez la documentation du service JOB PARSER dans le dossier `job-parser-service` du projet.