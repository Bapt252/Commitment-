# Guide de dépannage - Parser CV

Ce guide vous aide à résoudre les problèmes courants rencontrés avec le parsing de CV sur GitHub Pages.

## Problèmes avec les fichiers PDF

### Problème : Le contenu du PDF n'est pas correctement extrait

**Symptômes** : 
- Les informations extraites sont génériques et ne correspondent pas au contenu de votre CV
- Le nom affiché est "undefined Doe" ou ne correspond pas à votre nom

**Causes possibles** :
1. PDF.js n'a pas pu charger correctement
2. Votre PDF contient du texte sous forme d'images
3. Votre PDF utilise une mise en page complexe (colonnes multiples, éléments graphiques)

**Solutions** :
1. **Vérifiez la console du navigateur** pour les erreurs (F12 → onglet "Console")
2. **Essayez un PDF plus simple** avec une mise en page basique
3. **Convertissez votre CV en DOCX** et essayez à nouveau
4. **Renommez votre fichier** avec un format clair (ex: "CV_Prenom_Nom.pdf")

## Problèmes avec l'API OpenAI

### Problème : L'API OpenAI ne fonctionne pas

**Symptômes** :
- Message d'erreur concernant l'API
- Le système revient au mode simulation malgré une clé API fournie

**Causes possibles** :
1. Clé API invalide ou expirée
2. Quota d'API dépassé
3. Les restrictions du navigateur bloquent les requêtes API

**Solutions** :
1. **Vérifiez votre clé API** (elle doit commencer par "sk-")
2. **Vérifiez votre quota** sur le tableau de bord OpenAI
3. **Essayez de désactiver les bloqueurs de pub ou de cookies**
4. **Essayez dans une fenêtre de navigation privée**

## Problèmes d'extraction des noms

### Problème : Le nom extrait du fichier est incorrect

**Symptômes** :
- Le nom affiché ne correspond pas au nom dans le fichier
- Les formats particuliers comme "NOM_Prenom" ne sont pas reconnus

**Solutions** :
1. **Utilisez un format standard** : "CV_Prenom_Nom.pdf" ou "Prenom_Nom_CV.pdf"
2. **Testez différents formats de nom** sur la page de test : [test-cv-parser.html](test-cv-parser.html)
3. **Évitez les caractères spéciaux** dans le nom de fichier

## Tests simples pour identifier la source du problème

1. **Test d'extraction de nom** : Utilisez la page [test-cv-parser.html](test-cv-parser.html) pour vérifier si votre format de nom de fichier est correctement reconnu

2. **Test avec un fichier simple** : Essayez avec un fichier texte (.txt) contenant simplement votre nom, email et quelques compétences

3. **Test de l'API OpenAI** : Si vous avez une clé API, vérifiez qu'elle fonctionne en l'utilisant sur le site web d'OpenAI

## Solutions avancées

### Injection manuelle de données via la console (pour développeurs)

Si le parsing échoue complètement, vous pouvez injecter manuellement des données:

1. Ouvrez la console (F12 → onglet "Console")
2. Collez et exécutez le code suivant (modifiez les valeurs selon vos besoins):

```javascript
// Données personnalisées
const myData = {
  personal_info: {
    name: "Votre Nom",
    email: "votre.email@exemple.com",
    phone: "+33 6 12 34 56 78"
  },
  skills: ["JavaScript", "Python", "Management"],
  work_experience: [
    {
      title: "Développeur Senior",
      company: "MaCompagnie",
      start_date: "2020-01",
      end_date: "present"
    }
  ]
};

// Mise à jour de l'interface
document.getElementById('parsedName').textContent = myData.personal_info.name;
document.getElementById('parsedJobTitle').textContent = myData.work_experience[0].title;
document.getElementById('parsedEmail').textContent = myData.personal_info.email;
document.getElementById('parsedPhone').textContent = myData.personal_info.phone;
document.getElementById('parsedSkills').textContent = myData.skills.join(', ');
document.getElementById('parsedExperience').textContent = myData.work_experience.length + " expérience(s) professionnelle(s)";
```

## Contact et support

Si vous continuez à rencontrer des problèmes après avoir essayé ces solutions, n'hésitez pas à soumettre un problème sur le [dépôt GitHub](https://github.com/Bapt252/Commitment-/issues).
