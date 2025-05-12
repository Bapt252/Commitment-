#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Parser CLI avec GPT
-----------------------
Un outil en ligne de commande pour extraire des informations de fiches de poste en PDF en utilisant GPT.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import PyPDF2
import re
import openai  # Nouvelle importation

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("job-parser-cli-gpt")

# Configurer l'API OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY", "")  # Assurez-vous d'avoir défini cette variable d'environnement

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un fichier PDF."""
    logger.info(f"Extraction du texte du fichier PDF: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        
        logger.debug(f"Texte extrait ({len(text)} caractères)")
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
        raise

# Sauvegardons l'ancienne fonction d'extraction pour fallback
def extract_job_info_regex(text):
    """Extrait les informations d'une fiche de poste à partir du texte en utilisant des regex."""
    # Copiez l'intégralité de la fonction extract_job_info originale ici
    # ...
    
    # Dictionnaire pour stocker les informations extraites
    job_info = {
        "titre_poste": "",
        "entreprise": "",
        "localisation": "",
        "type_contrat": "",
        "competences": [],
        "experience": "",
        "formation": "",
        "salaire": "",
        "description": "",
        "date_publication": "",
    }
    
    # Extraction du titre du poste
    title_patterns = [
        r"(?:^|\n)[\s•]*Poste[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Intitulé du poste[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Offre d'emploi[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*([\w\s\-']+(?:développeur|ingénieur|technicien|consultant|manager|responsable|directeur|analyste)[\w\s\-']+)(?:\n|$)"
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, text, re.IGNORECASE)
        if title_match:
            job_info["titre_poste"] = title_match.group(1).strip()
            break
    
    # Extraction du nom de l'entreprise
    company_patterns = [
        r"(?:^|\n)[\s•]*Entreprise[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Société[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Employeur[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in company_patterns:
        company_match = re.search(pattern, text, re.IGNORECASE)
        if company_match:
            job_info["entreprise"] = company_match.group(1).strip()
            break
    
    # Extraction de la localisation
    location_patterns = [
        r"(?:^|\n)[\s•]*Lieu[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Localisation[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Localité[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Ville[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in location_patterns:
        location_match = re.search(pattern, text, re.IGNORECASE)
        if location_match:
            job_info["localisation"] = location_match.group(1).strip()
            break
    
    # Extraction du type de contrat
    contract_patterns = [
        r"(?:^|\n)[\s•]*Type de contrat[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Contrat[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*(CDI|CDD|Stage|Alternance|Intérim|Freelance)(?:\n|$)"
    ]
    
    for pattern in contract_patterns:
        contract_match = re.search(pattern, text, re.IGNORECASE)
        if contract_match:
            job_info["type_contrat"] = contract_match.group(1).strip()
            break
    
    # Extraction des compétences requises
    skills_patterns = [
        r"(?:^|\n)[\s•]*Compétences[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Compétences requises[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Compétences techniques[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Qualifications[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Prérequis[\s:]*(.+?)(?:\n\n|$)"
    ]
    
    for pattern in skills_patterns:
        skills_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            # Extraction des compétences en les séparant par saut de ligne ou par des puces
            skills = re.split(r'[\n•,]', skills_text)
            # Filtrer les compétences vides
            job_info["competences"] = [skill.strip() for skill in skills if skill.strip()]
            break
    
    # Extraction de l'expérience requise
    exp_patterns = [
        r"(?:^|\n)[\s•]*Expérience[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Années d'expérience[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*([\d]+[\s]*ans d'expérience)(?:\n|$)",
        r"(?:^|\n)[\s•]*Expérience requise[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in exp_patterns:
        exp_match = re.search(pattern, text, re.IGNORECASE)
        if exp_match:
            job_info["experience"] = exp_match.group(1).strip()
            break
    
    # Extraction de la formation requise
    edu_patterns = [
        r"(?:^|\n)[\s•]*Formation[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Diplôme[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Niveau d'études[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Éducation[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in edu_patterns:
        edu_match = re.search(pattern, text, re.IGNORECASE)
        if edu_match:
            job_info["formation"] = edu_match.group(1).strip()
            break
    
    # Extraction du salaire
    salary_patterns = [
        r"(?:^|\n)[\s•]*Salaire[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Rémunération[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Package[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*\€[\s]*(.+?)(?:\n|$)"
    ]
    
    for pattern in salary_patterns:
        salary_match = re.search(pattern, text, re.IGNORECASE)
        if salary_match:
            job_info["salaire"] = salary_match.group(1).strip()
            break
    
    # Extraction de la description du poste
    desc_patterns = [
        r"(?:^|\n)[\s•]*Description[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Description du poste[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Missions[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Responsabilités[\s:]*(.+?)(?:\n\n|$)"
    ]
    
    for pattern in desc_patterns:
        desc_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if desc_match:
            job_info["description"] = desc_match.group(1).strip()
            break
    
    # Extraire la date de publication si présente
    date_patterns = [
        r"(?:^|\n)[\s•]*Date[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Publié le[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Date de publication[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            job_info["date_publication"] = date_match.group(1).strip()
            break
    
    return job_info

def extract_job_info(text):
    """Extrait les informations d'une fiche de poste en utilisant GPT."""
    logger.info("Extraction des informations avec GPT...")
    
    if not openai.api_key:
        logger.warning("Clé API OpenAI non définie. Utilisation de l'extraction par regex.")
        return extract_job_info_regex(text)
    
    # Si le texte est trop long, le tronquer
    max_tokens = 15000  # Approximativement 15000 caractères
    if len(text) > max_tokens:
        logger.warning(f"Texte trop long ({len(text)} caractères), troncature à {max_tokens} caractères")
        text = text[:max_tokens] + "...[texte tronqué]"
    
    # Définir le prompt pour l'extraction d'information structurée
    prompt = f"""
Tu es un expert en analyse de fiches de poste pour l'industrie du recrutement.
Tu dois extraire avec précision toutes les informations importantes d'une fiche de poste.

INSTRUCTIONS IMPÉRATIVES:
1. Extrait UNIQUEMENT les informations réellement présentes dans la fiche de poste.
2. Ne génère JAMAIS d'informations fictives.
3. Pour tout champ non présent dans la fiche de poste, renvoie une valeur vide.
4. Sois particulièrement attentif au titre du poste, à l'entreprise, au lieu de travail et au type de contrat.

FICHE DE POSTE À ANALYSER:
{text}

Extrais les informations suivantes au format JSON et seulement au format JSON (aucun texte avant ou après) :
{{
  "titre_poste": "",  // Titre du poste
  "entreprise": "",   // Nom de l'entreprise
  "localisation": "", // Lieu de travail
  "type_contrat": "", // Type de contrat (CDI, CDD, etc.)
  "competences": [],  // Liste des compétences requises
  "experience": "",   // Expérience requise
  "formation": "",    // Formation requise
  "salaire": "",      // Salaire proposé
  "description": "",  // Description du poste
  "date_publication": "" // Date de publication
}}
"""
    
    try:
        # Appel à l'API OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # ou un autre modèle disponible
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de fiches de poste."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        # Extraire la réponse
        response_text = response.choices[0].message.content
        logger.debug(f"Réponse GPT: {response_text}")
        
        # Tentative d'extraire un JSON de la réponse
        try:
            # Nettoyage du texte pour s'assurer qu'il ne contient que du JSON
            json_pattern = r'(\{[\s\S]*\})' 
            match = re.search(json_pattern, response_text)
            if match:
                json_str = match.group(1)
                parsed_result = json.loads(json_str)
                logger.info("Parsing JSON réussi")
                return parsed_result
            else:
                # Essayer de parser directement si l'extraction a échoué
                parsed_result = json.loads(response_text)
                return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            logger.info("Utilisation de l'extraction par regex comme fallback")
            return extract_job_info_regex(text)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
        logger.info("Utilisation de l'extraction par regex comme fallback")
        return extract_job_info_regex(text)

def parse_job_posting(pdf_path):
    """Parse une fiche de poste PDF et en extrait les informations."""
    try:
        # Extraire le texte du PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Extraire les informations du texte
        job_info = extract_job_info(text)
        
        # Ajouter des métadonnées sur le parsing
        result = {
            "parsing_metadata": {
                "pdf_path": pdf_path,
                "filename": os.path.basename(pdf_path),
                "parsed_at": datetime.now().isoformat(),
                "parser_version": "1.0.0-gpt"
            },
            "job_info": job_info
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors du parsing: {str(e)}")
        raise

def main():
    """Fonction principale du script."""
    # Définition des arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Parser GPT pour fiches de poste en PDF')
    parser.add_argument('pdf_path', help='Chemin vers le fichier PDF de la fiche de poste')
    parser.add_argument('--output', '-o', help='Chemin pour enregistrer le résultat JSON (optionnel)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Activer le mode verbeux')
    parser.add_argument('--api-key', '-k', help='Clé API OpenAI (optionnel, peut aussi être définie via OPENAI_API_KEY)')
    
    args = parser.parse_args()
    
    # Configuration du niveau de log en fonction de l'option verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Configurer la clé API si fournie
    if args.api_key:
        openai.api_key = args.api_key
    
    # Vérifier que le fichier existe
    if not os.path.exists(args.pdf_path):
        logger.error(f"Erreur: Le fichier {args.pdf_path} n'existe pas.")
        return 1
    
    # Vérifier l'extension du fichier
    if not args.pdf_path.lower().endswith('.pdf'):
        logger.warning(f"Attention: Le fichier {args.pdf_path} ne semble pas être un PDF.")
    
    try:
        logger.info(f"Analyse du fichier: {args.pdf_path}")
        
        # Parser la fiche de poste
        result = parse_job_posting(args.pdf_path)
        
        # Définir le nom du fichier de sortie
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = os.path.basename(args.pdf_path)
            output_file = f"job-parsing-gpt-result-{timestamp}-{filename}.json"
        
        # Sauvegarder le résultat dans un fichier JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Afficher un résumé des informations extraites
        job_info = result["job_info"]
        print("\n--- Résultat du parsing GPT ---")
        print(f"Titre du poste: {job_info.get('titre_poste', 'Non détecté')}")
        print(f"Entreprise: {job_info.get('entreprise', 'Non détectée')}")
        
        if job_info.get('localisation'):
            print(f"Localisation: {job_info.get('localisation')}")
        
        if job_info.get('type_contrat'):
            print(f"Type de contrat: {job_info.get('type_contrat')}")
        
        if job_info.get('competences'):
            if isinstance(job_info.get('competences'), list):
                competences = job_info.get('competences')
                if competences and len(competences) > 0:
                    print(f"Compétences: {', '.join(competences)}")
                else:
                    print("Compétences: Non détectées")
            else:
                print(f"Compétences: {job_info.get('competences')}")
        else:
            print("Compétences: Non détectées")
        
        if job_info.get('experience'):
            print(f"Expérience: {job_info.get('experience')}")
            
        if job_info.get('formation'):
            print(f"Formation: {job_info.get('formation')}")
            
        if job_info.get('salaire'):
            print(f"Salaire: {job_info.get('salaire')}")
        
        print(f"\nRésultat complet sauvegardé dans: {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
