#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Parser CLI
-------------
Un outil en ligne de commande pour extraire des informations de fiches de poste en PDF.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import PyPDF2
import re

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("job-parser-cli")

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

def extract_job_info(text):
    """Extrait les informations d'une fiche de poste à partir du texte."""
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
    
    # Extraction directe des types de contrat courants
    contract_types = ["CDI", "CDD", "Stage", "Alternance", "Intérim", "Freelance"]
    for contract_type in contract_types:
        if re.search(r'\b' + re.escape(contract_type) + r'\b', text, re.IGNORECASE):
            if not job_info["type_contrat"]:
                job_info["type_contrat"] = contract_type
    
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
    
    # Si aucune compétence n'a été trouvée, rechercher des technologies courantes
    if not job_info["competences"]:
        tech_skills = [
            "JavaScript", "React", "Angular", "Vue.js", "Node.js", "Python", "Django", "Flask",
            "Java", "Spring", "Hibernate", "C#", ".NET", "PHP", "Laravel", "Symfony",
            "Ruby", "Rails", "Go", "Rust", "Kotlin", "Swift", "SQL", "MySQL", "PostgreSQL",
            "MongoDB", "Redis", "Elasticsearch", "GraphQL", "REST", "SOAP", "HTML", "CSS",
            "Sass", "Less", "Bootstrap", "Tailwind", "Material-UI", "AWS", "Azure", "GCP",
            "Docker", "Kubernetes", "Jenkins", "GitHub Actions", "GitLab CI", "Git", "SVN",
            "Jira", "Confluence", "Agile", "Scrum", "Kanban", "TDD", "BDD", "DevOps", "CI/CD"
        ]
        
        found_skills = []
        for skill in tech_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        if found_skills:
            job_info["competences"] = found_skills
    
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
    
    # Si aucune description n'a été trouvée, tenter une extraction plus générale
    if not job_info["description"]:
        # Prendre les premiers paragraphes du texte comme description
        paragraphs = re.split(r'\n\n+', text)
        if len(paragraphs) > 1:
            # Ignorer le premier paragraphe qui contient souvent le titre
            job_info["description"] = " ".join(paragraphs[1:3])
    
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
                "parser_version": "1.0.0"
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
    parser = argparse.ArgumentParser(description='Parser pour fiches de poste en PDF')
    parser.add_argument('pdf_path', help='Chemin vers le fichier PDF de la fiche de poste')
    parser.add_argument('--output', '-o', help='Chemin pour enregistrer le résultat JSON (optionnel)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Activer le mode verbeux')
    
    args = parser.parse_args()
    
    # Configuration du niveau de log en fonction de l'option verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
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
            output_file = f"job-parsing-result-{timestamp}-{filename}.json"
        
        # Sauvegarder le résultat dans un fichier JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Afficher un résumé des informations extraites
        job_info = result["job_info"]
        print("\n--- Résultat du parsing ---")
        print(f"Titre du poste: {job_info.get('titre_poste', 'Non détecté')}")
        print(f"Entreprise: {job_info.get('entreprise', 'Non détectée')}")
        
        if job_info.get('localisation'):
            print(f"Localisation: {job_info.get('localisation')}")
        
        if job_info.get('type_contrat'):
            print(f"Type de contrat: {job_info.get('type_contrat')}")
        
        if job_info.get('competences'):
            print(f"Compétences: {', '.join(job_info.get('competences'))}")
        else:
            print("Compétences: Non détectées")
        
        if job_info.get('experience'):
            print(f"Expérience: {job_info.get('experience')}")
        
        print(f"\nRésultat complet sauvegardé dans: {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
