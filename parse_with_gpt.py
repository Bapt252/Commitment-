#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import PyPDF2
import requests
from datetime import datetime

print("\n=== SCRIPT DIRECT PARSER GPT ===\n")

# La clé API OpenAI sera fournie en argument ou via une variable d'environnement
API_KEY = None  # sera défini lors de l'exécution

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un fichier PDF."""
    print(f"Extraction du texte du fichier: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        
        print(f"Texte extrait: {len(text)} caractères")
        return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte: {str(e)}")
        raise

def analyze_with_gpt(text, api_key):
    """Analyse le texte avec l'API OpenAI."""
    print("Envoi du texte à l'API OpenAI (GPT)...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system", 
                "content": "Tu es un expert en analyse de fiches de poste."
            },
            {
                "role": "user",
                "content": f"""
Analyse cette fiche de poste et extrait les informations importantes.
Réponds UNIQUEMENT au format JSON.

FICHE DE POSTE:
{text}

RÉPONDS AU FORMAT JSON EXACTEMENT COMME CECI:
{{
  "titre_poste": "",
  "entreprise": "",
  "localisation": "",
  "type_contrat": "",
  "competences": [],
  "experience": "",
  "formation": "",
  "salaire": "",
  "description": ""
}}
"""
            }
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"Erreur API: {response.status_code}")
            print(response.text)
            return None
            
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Tenter de parser le JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("Erreur: Impossible de parser la réponse JSON")
            print("Réponse:", content)
            return None
            
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API: {str(e)}")
        return None

def main():
    # Vérifier si un chemin de fichier a été fourni
    if len(sys.argv) < 2:
        print("Usage: python parse_with_gpt.py chemin/vers/fichier.pdf [--api-key VOTRE_CLE_API]")
        return 1
        
    pdf_path = sys.argv[1]
    
    # Récupérer la clé API
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Chercher l'argument --api-key
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--api-key" and i+1 < len(sys.argv):
            api_key = sys.argv[i+1]
    
    if not api_key:
        print("ERREUR: Clé API OpenAI non trouvée.")
        print("Veuillez fournir une clé API avec --api-key ou définir la variable d'environnement OPENAI_API_KEY")
        return 1
    
    # Vérifier que le fichier existe
    if not os.path.exists(pdf_path):
        print(f"Erreur: Le fichier {pdf_path} n'existe pas.")
        return 1
    
    try:
        # Extraire le texte
        text = extract_text_from_pdf(pdf_path)
        
        # Analyser avec GPT
        result = analyze_with_gpt(text, api_key)
        
        if not result:
            print("Impossible d'analyser la fiche de poste.")
            return 1
            
        # Sauvegarder le résultat
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f"job-gpt-result-{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        # Afficher le résultat
        print("\n=== RÉSULTAT DU PARSING AVEC GPT ===\n")
        print(f"Titre du poste: {result.get('titre_poste', 'Non détecté')}")
        print(f"Entreprise: {result.get('entreprise', 'Non détectée')}")
        print(f"Localisation: {result.get('localisation', 'Non détectée')}")
        print(f"Type de contrat: {result.get('type_contrat', 'Non détecté')}")
        
        if isinstance(result.get('competences'), list) and result.get('competences'):
            print(f"Compétences: {', '.join(result.get('competences'))}")
        else:
            print("Compétences: Non détectées")
            
        print(f"Expérience: {result.get('experience', 'Non détectée')}")
        print(f"Formation: {result.get('formation', 'Non détectée')}")
        print(f"Salaire: {result.get('salaire', 'Non détecté')}")
        
        print(f"\nRésultat complet sauvegardé dans: {output_file}")
        return 0
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
