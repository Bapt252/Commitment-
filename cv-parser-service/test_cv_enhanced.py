#!/usr/bin/env python3
"""
Script de test pour l'analyse améliorée de CV
"""

import os
import json
import openai

# Prompts améliorés pour l'extraction CV et le focus sur les expériences
SYSTEM_PROMPT = """
Tu es un assistant spécialisé dans l'extraction précise d'informations de CV pour le projet Commitment. Ta tâche principale est d'analyser le CV fourni et d'en extraire les informations structurées selon un format JSON spécifique.

## RÈGLES GÉNÉRALES
- Extrais UNIQUEMENT les informations explicitement présentes dans le CV.
- N'invente JAMAIS d'informations.
- Utilise une chaîne vide ou liste vide pour tout champ sans information explicite.
- Respecte scrupuleusement le format JSON demandé.

## FORMAT DE SORTIE JSON
{
  "nom": string,
  "prenom": string,
  "poste": string,
  "adresse": string,
  "email": string,
  "telephone": string,
  "competences": [string],
  "logiciels": [string],
  "soft_skills": [string],
  "experiences": [
    {
      "titre": string,
      "entreprise": string,
      "lieu": string,
      "date_debut": string,  // Format ISO "YYYY-MM"
      "date_fin": string | "Present",  // Format ISO "YYYY-MM" ou "Present"
      "description": string,
      "responsabilites": [string],  // Liste des responsabilités spécifiques
      "realisations": [string],  // Liste des réalisations quantifiables
      "technologies": [string],  // Technologies mentionnées dans cette expérience
      "taille_equipe": number | "",
      "type_contrat": string | ""  // CDI, CDD, Freelance, Stage, etc.
    }
  ],
  "formation": [
    {
      "diplome": string,
      "etablissement": string,
      "lieu": string,
      "date_debut": string,  // Format ISO "YYYY-MM"
      "date_fin": string,    // Format ISO "YYYY-MM"
      "description": string,
      "distinctions": [string]
    }
  ],
  "certifications": [
    {
      "nom": string,
      "organisme": string,
      "date_obtention": string,
      "date_expiration": string | "No Expiration"
    }
  ]
}

## INSTRUCTIONS SPÉCIALES POUR LES EXPÉRIENCES PROFESSIONNELLES
1. PRÉCISION TEMPORELLE:
   - Convertis toutes les dates au format "YYYY-MM"
   - Ex: "Janvier 2022" → "2022-01", "Mars 2020" → "2020-03"
   - Si seule l'année est mentionnée, utilise le mois de janvier: "2019" → "2019-01"
   - Pour les expériences en cours, utilise exactement "Present" pour le champ date_fin

2. DÉCOMPOSITION STRUCTURÉE:
   - Distingue clairement entre:
     * "description": résumé général du poste ou de la mission
     * "responsabilites": tâches et activités régulières (utilise des verbes d'action)
     * "realisations": résultats concrets et mesurables (avec des métriques si possible)

3. EXTRACTION TECHNOLOGIQUE:
   - Identifie toutes les technologies, frameworks, outils, méthodologies mentionnés dans chaque expérience
   - Standardise les noms (ex: "React.js" → "React", "Tensorflow" → "TensorFlow")

4. ANALYSE CONTEXTUELLE:
   - Détecte le type de contrat (CDI, CDD, Freelance, Stage) à partir du contexte
   - Identifie la taille d'équipe lorsqu'elle est mentionnée, même indirectement
   - Extrais le lieu précis de l'expérience (ville et pays si disponible)

5. ORDRE CHRONOLOGIQUE:
   - Place les expériences dans l'ordre chronologique inversé (la plus récente en premier)

Réponds UNIQUEMENT avec un objet JSON valide correspondant au format demandé, sans aucun texte avant ou après.
"""

def extract_text_from_pdf(file_path):
    """Extrait le texte d'un fichier PDF."""
    try:
        from PyPDF2 import PdfReader
        
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
        return None

def analyze_cv_with_gpt(cv_text):
    """Analyse un CV avec GPT-4o-mini et le prompt système amélioré."""
    # Vérifier que la clé API est définie
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("ERREUR: La variable d'environnement OPENAI_API_KEY n'est pas définie")
        return None

    try:
        # Détection de la version d'OpenAI et appel adapté
        if hasattr(openai, 'ChatCompletion'):
            # Version plus ancienne (<=3.x)
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": cv_text}
                ],
                temperature=0.1
            )
            if hasattr(response.choices[0], 'message'):
                content = response.choices[0].message.content
            else:
                content = response.choices[0].message['content']
        else:
            # Version plus récente (>=4.x)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": cv_text}
                ],
                temperature=0.1
            )
            content = response.choices[0].message.content
        
        # Nettoyer le contenu
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Extraire uniquement la partie JSON si nécessaire
        json_start = content.find('{')
        json_end = content.rfind('}')
        if json_start >= 0 and json_end > json_start:
            content = content[json_start:json_end+1]
        
        # Parser le JSON
        return json.loads(content)
        
    except Exception as e:
        print(f"Erreur lors de l'analyse du CV: {str(e)}")
        return None

def main():
    # Vérifier les arguments
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_cv_enhanced.py chemin/vers/votre/cv.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Vérifier que le fichier existe
    if not os.path.exists(file_path):
        print(f"ERREUR: Le fichier {file_path} n'existe pas")
        sys.exit(1)
    
    # Extraire le texte du CV
    print(f"Extraction du texte du fichier {file_path}...")
    cv_text = extract_text_from_pdf(file_path)
    
    if not cv_text:
        print("ERREUR: Impossible d'extraire le texte du CV")
        sys.exit(1)
    
    print(f"Texte extrait avec succès ({len(cv_text)} caractères)")
    
    # Analyser le CV
    print("Analyse du CV avec GPT-4o-mini...")
    cv_data = analyze_cv_with_gpt(cv_text)
    
    if not cv_data:
        print("ERREUR: Échec de l'analyse du CV")
        sys.exit(1)
    
    # Enregistrer les résultats dans un fichier JSON
    output_path = os.path.splitext(file_path)[0] + "_enhanced_parsed.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nRésultats enregistrés dans {output_path}")
    
    # Afficher un résumé des données extraites
    print("\n=== RÉSUMÉ DES DONNÉES EXTRAITES ===")
    print(f"Nom: {cv_data.get('prenom', '')} {cv_data.get('nom', '')}")
    print(f"Poste: {cv_data.get('poste', '')}")
    print(f"Email: {cv_data.get('email', '')}")
    print(f"Téléphone: {cv_data.get('telephone', '')}")
    
    # Afficher les expériences
    print("\n=== EXPÉRIENCES PROFESSIONNELLES ===")
    for i, exp in enumerate(cv_data.get('experiences', []), 1):
        print(f"\n[{i}] {exp.get('titre', '')} - {exp.get('entreprise', '')}")
        print(f"    {exp.get('date_debut', '')} → {exp.get('date_fin', 'Present')}")
        print(f"    Technologies: {', '.join(exp.get('technologies', []))}")
        if exp.get('responsabilites'):
            print(f"    Responsabilités: {len(exp.get('responsabilites', []))} tâches identifiées")
        if exp.get('realisations'):
            print(f"    Réalisations: {len(exp.get('realisations', []))} accomplissements identifiés")

if __name__ == "__main__":
    main()
