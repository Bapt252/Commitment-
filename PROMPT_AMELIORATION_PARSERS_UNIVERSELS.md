# 🚀 PROMPT : Amélioration des Parsers pour Support Multi-formats

Copie ce prompt dans une nouvelle conversation pour implémenter le support multi-formats :

---

**CONTEXTE DU PROJET :**

Je travaille sur **Commitment**, un système de matching CV/emploi basé sur **SuperSmartMatch V2.1 Enhanced**. 

**Architecture actuelle :**
- **Repository GitHub :** https://github.com/Bapt252/Commitment-
- **CV Parser V2** (port 5051) : Parse les CV en PDF
- **Job Parser V2** (port 5053) : Parse les fiches de poste en PDF  
- **API Enhanced V2.1** (port 5055) : Moteur de matching intelligent
- **Technologies :** Python Flask, OpenAI GPT-4o-mini, Docker, Redis, PostgreSQL

**SuperSmartMatch V2.1 Enhanced** inclut :
- Détection automatique des domaines métiers
- Matrice de compatibilité des domaines  
- Système d'alertes intelligent
- Pondérations optimisées (25% compatibilité métier, 30% missions, 25% compétences, 10% expérience, 10% qualité)

**PROBLÈME ACTUEL :**

Les parsers CV et Job retournent actuellement :
```json
{"error":"Seuls les fichiers PDF sont acceptés"}
```

**Formats testés qui échouent :**
- ❌ Fichiers Word (.docx, .doc)
- ❌ Images (PNG, JPG) 
- ❌ Texte (.txt)
- ❌ Autres formats courants

**OBJECTIF :**

Créer des **parsers universels** qui peuvent traiter :
- ✅ **PDF** (déjà fonctionnel)
- ✅ **Word** (.docx, .doc)
- ✅ **Images** (PNG, JPG, JPEG) avec OCR
- ✅ **Texte** (.txt)
- ✅ **HTML** 
- ✅ **RTF**
- ✅ **OpenOffice** (.odt)

**SPÉCIFICATIONS TECHNIQUES :**

**Structure actuelle des parsers :**
```
cv-parser-v2/
├── app.py                 # Flask app principal
├── parsers/
│   ├── enhanced-mission-parser.js
│   └── fix_pdf_extraction.py
└── requirements.txt

job-parser-v2/  
├── app.py                 # Flask app principal
└── requirements.txt
```

**Endpoints actuels :**
- `POST /api/parse-cv/` (CV Parser)
- `POST /api/parse-job` (Job Parser)
- `GET /health` (les deux)

**Format de réponse attendu (à conserver) :**
```json
{
  "status": "success",
  "data": {
    "candidate_name": "...",
    "personal_info": {...},
    "professional_experience": [...],
    "technical_skills": [...],
    "soft_skills": [...],
    // ...
  }
}
```

**CONTRAINTES :**

1. **Rétrocompatibilité** : Les PDF doivent continuer à fonctionner
2. **Performance** : Pas de dégradation pour les PDF existants
3. **Qualité** : Même niveau d'extraction qu'actuellement
4. **API** : Garder les mêmes endpoints et formats de réponse
5. **Docker** : Solutions compatibles avec l'architecture Docker existante

**APPROCHE SUGGÉRÉE :**

1. **Détection automatique du format** via mimetype
2. **Conversion universelle vers texte** selon le format
3. **Pipeline unifié** : Format → Texte → Parsing GPT-4o-mini
4. **Fallback PDF** : Si échec, convertir vers PDF puis parser

**TECHNOLOGIES RECOMMANDÉES :**
- **python-magic** : Détection format
- **python-docx** : Word
- **Pillow + pytesseract** : OCR images
- **Beautiful Soup** : HTML
- **striprtf** : RTF
- **odfpy** : OpenOffice

**QUESTION :**

Peux-tu créer une version améliorée des parsers CV et Job qui :

1. **Détecte automatiquement le format** du fichier uploadé
2. **Extrait le texte** selon le format approprié
3. **Maintient la même qualité** de parsing qu'actuellement
4. **Conserve l'API existante** (rétrocompatibilité)
5. **Gère les erreurs** gracieusement avec fallbacks

**Fournis :**
- Code Python complet pour les parsers universels
- Configuration Docker si nécessaire  
- Tests pour valider le multi-format
- Documentation d'installation des dépendances

**CONTEXTE DE PERFORMANCE :**
Le système traite actuellement des CV comme celui de Zachary (profil commercial) et des fiches de poste (comptable, gestionnaire paie, assistant juridique). Les parsers doivent extraire suffisamment d'informations pour que SuperSmartMatch V2.1 Enhanced puisse calculer des scores de matching précis.

**PRIORITÉ :** High - Cela résoudra un goulot d'étranglement majeur dans notre workflow de test et production.

---

**FIN DU PROMPT** 📋
