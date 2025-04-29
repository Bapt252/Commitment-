# Guide d'utilisation du parsing de CV sur GitHub Pages

Ce guide vous explique comment utiliser efficacement le parsing de CV sur la page de chargement de CV hébergée sur GitHub Pages.

## Solution implémentée

Le parsing de CV sur GitHub Pages peut fonctionner de deux manières :

1. **Mode simulation** : Génère des données fictives basées sur le nom du fichier
2. **Mode réel avec OpenAI** : Utilise l'API OpenAI pour analyser votre CV (nécessite une clé API)

## Comment utiliser le parsing de CV

### Utilisation sans clé API (Mode simulation)

Si vous n'avez pas de clé API OpenAI, le système fonctionnera en mode simulation :

1. Cliquez sur la zone de dépôt ou faites glisser votre fichier CV
2. Un traitement simulé sera effectué
3. Des données fictives seront générées en se basant sur le nom de votre fichier
   - Par exemple, si votre fichier s'appelle "CV_Jean_Dupont.pdf", le système extraira "Jean Dupont" comme nom
   - Si le nom de fichier contient "dev", "marketing", "data" ou d'autres mots-clés, le système générera des compétences pertinentes

### Utilisation avec une clé API OpenAI (Mode réel)

Pour obtenir un parsing de CV précis et réel, vous pouvez utiliser votre propre clé API OpenAI :

1. Sur la page de chargement de CV, vous verrez une section "Clé API OpenAI (facultatif)"
2. Entrez votre clé API OpenAI (commençant par "sk-")
3. Cliquez sur "Enregistrer"
4. Chargez ensuite votre CV comme d'habitude
5. Le système utilisera l'API OpenAI pour analyser réellement le contenu de votre CV

> **Note de sécurité** : Votre clé API est stockée uniquement dans le stockage local de votre navigateur et n'est jamais envoyée à nos serveurs. Elle est utilisée uniquement pour communiquer directement avec l'API OpenAI depuis votre navigateur.

## Fonctionnalités du parsing de CV

Que vous utilisiez le mode simulation ou le mode réel, le système extrait les informations suivantes :

- **Informations personnelles** : Nom, email, téléphone
- **Titre de poste actuel** : Basé sur votre expérience la plus récente
- **Compétences techniques** : Liste des compétences détectées dans votre CV
- **Expérience professionnelle** : Résumé de votre expérience professionnelle

## Assistant de conversation IA

Après l'analyse de votre CV, vous pouvez utiliser l'assistant IA pour discuter de votre profil :

1. Cliquez sur le bouton "Discuter de mon CV avec l'IA"
2. Un chat s'ouvrira avec un assistant IA
3. Vous pouvez poser des questions comme :
   - Comment puis-je améliorer mon CV ?
   - Quelles sont mes forces ?
   - Quelles compétences devrais-je développer ?
   - Quels types d'emploi me correspondent ?

Si vous avez fourni une clé API OpenAI, l'assistant utilisera GPT pour générer des réponses personnalisées. Sinon, des réponses prédéfinies seront utilisées.

## Résolution des problèmes courants

### Le parsing ne fonctionne pas correctement

- **Vérifiez le format du fichier** : Assurez-vous que votre CV est au format PDF, DOCX, DOC, JPG ou PNG
- **Vérifiez la taille du fichier** : Le fichier ne doit pas dépasser 10 MB
- **Essayez un autre format** : Si votre PDF pose problème, essayez de convertir votre CV en DOCX

### Problèmes avec l'API OpenAI

- **Vérifiez votre clé API** : Assurez-vous qu'elle commence par "sk-" et qu'elle est valide
- **Crédit épuisé** : Vérifiez que votre compte OpenAI dispose encore de crédits
- **Erreur d'API** : En cas d'erreur, le système reviendra automatiquement au mode simulation

## Prochaines étapes

Après avoir chargé et analysé votre CV, vous pouvez :

1. Cliquer sur "Continuer" pour passer au questionnaire
2. Les données extraites de votre CV seront utilisées pour pré-remplir votre profil dans les étapes suivantes

## Remarques importantes

- La qualité du parsing avec l'API OpenAI dépend du format et de la clarté de votre CV
- Les fichiers PDF complexes avec plusieurs colonnes peuvent être moins bien analysés
- Pour de meilleurs résultats, utilisez des CV au format simple et bien structuré
