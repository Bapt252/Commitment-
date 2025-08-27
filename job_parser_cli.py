#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Parser CLI
-------------
Un outil en ligne de commande pour extraire des informations de fiches de poste en PDF.
Version améliorée pour mieux capturer les informations spécifiques à différents formats de fiches de poste.
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
        
        # Journalisation du texte extrait si en mode très verbeux
        logger.debug(f"Texte extrait ({len(text)} caractères)")
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug("Aperçu du texte extrait :")
            logger.debug(text[:500] + "..." if len(text) > 500 else text)
        
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
        raise

def extract_job_info(text):
    """Extrait les informations d'une fiche de poste à partir du texte."""
    # Journalisation pour le débogage
    logger.debug("Extraction des informations du texte...")
    
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
    
    # Extraction du titre du poste - Patterns améliorés
    title_patterns = [
        r"(?:^|\n)[\s•]*Poste[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Intitulé du poste[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Offre d'emploi[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*([\w\s\-']+(?:développeur|ingénieur|technicien|consultant|manager|responsable|directeur|analyste)[\w\s\-']+)(?:\n|$)",
        # Nouveaux patterns
        r"^([^\n]{10,100})\n",  # Première ligne du document (si entre 10 et 100 caractères)
        r"(?:^|\n)[\s•]*Assistant[\s]+(?:de|d'|du|des)?[\s]*([^\n]+)",  # Postes commençant par "Assistant"
        r"(?:^|\n)[\s•]*Chargé[\s]+(?:de|d'|du|des)?[\s]*([^\n]+)",  # Postes commençant par "Chargé"
        r"(?:^|\n)[\s•]*Responsable[\s]+(?:de|d'|du|des)?[\s]*([^\n]+)",  # Postes commençant par "Responsable"
        r"(?:^|\n)[\s•]*Chef[\s]+(?:de|d'|du|des)?[\s]*([^\n]+)"  # Postes commençant par "Chef"
    ]
    
    # Si le titre n'est pas détecté par les patterns, essayer d'extraire la première ligne substantielle
    title_detected = False
    for pattern in title_patterns:
        title_match = re.search(pattern, text, re.IGNORECASE)
        if title_match:
            potential_title = title_match.group(1).strip()
            # Vérifie que le titre a une longueur raisonnable et ne contient pas juste des caractères de formatage
            if len(potential_title) > 5 and not re.match(r'^[\s\-•:]+$', potential_title):
                job_info["titre_poste"] = potential_title
                title_detected = True
                logger.debug(f"Titre détecté via pattern: {pattern}")
                logger.debug(f"Titre: {potential_title}")
                break
    
    # Si aucun titre détecté, chercher dans les premières lignes
    if not title_detected:
        logger.debug("Aucun titre détecté via patterns, recherche dans les premières lignes...")
        first_lines = text.split('\n')[:5]  # Considère les 5 premières lignes
        for line in first_lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100 and not re.match(r'^[\s\-•:]+$', line):
                job_info["titre_poste"] = line
                logger.debug(f"Titre extrait de la première ligne substantielle: {line}")
                break
    
    # Extraction du nom de l'entreprise - Patterns améliorés
    company_patterns = [
        r"(?:^|\n)[\s•]*Entreprise[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Société[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Employeur[\s:]*(.+?)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Nom de l'entreprise[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Cabinet[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Groupe[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Recruteur[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in company_patterns:
        company_match = re.search(pattern, text, re.IGNORECASE)
        if company_match:
            job_info["entreprise"] = company_match.group(1).strip()
            logger.debug(f"Entreprise détectée: {job_info['entreprise']}")
            break
    
    # Extraction de la localisation - Patterns améliorés
    location_patterns = [
        r"(?:^|\n)[\s•]*Lieu[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Localisation[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Localité[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Ville[\s:]*(.+?)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Lieu de travail[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Adresse[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Emplacement[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Basé à[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Basé[e]? en[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*([\w\s-]+ \(\d{5}\))",  # Format: Ville (Code postal)
        r"(?:^|\n)[\s•]*Issy[\s-]+les[\s-]+Moulineaux[\s\(\d\)]*"  # Spécifique à Issy-les-Moulineaux
    ]
    
    for pattern in location_patterns:
        location_match = re.search(pattern, text, re.IGNORECASE)
        if location_match:
            job_info["localisation"] = location_match.group(1).strip()
            logger.debug(f"Localisation détectée: {job_info['localisation']}")
            break
    
    # Extraction du type de contrat - Patterns améliorés
    contract_patterns = [
        r"(?:^|\n)[\s•]*Type de contrat[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Contrat[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*(CDI|CDD|Stage|Alternance|Intérim|Freelance)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Type d'emploi[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Statut[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*(CDD de \d+ mois)",  # Format: CDD de X mois
        r"(?:^|\n)[\s•]*(CDD \d+ mois)",  # Format: CDD X mois
        r"(?:^|\n)[\s•]*(CDD.*?\(\d+h\/semaine\))"  # Format: CDD ... (Xh/semaine)
    ]
    
    for pattern in contract_patterns:
        contract_match = re.search(pattern, text, re.IGNORECASE)
        if contract_match:
            job_info["type_contrat"] = contract_match.group(1).strip()
            logger.debug(f"Type de contrat détecté: {job_info['type_contrat']}")
            break
    
    # Extraction directe des types de contrat courants
    if not job_info["type_contrat"]:
        contract_types = ["CDI", "CDD", "Stage", "Alternance", "Intérim", "Freelance"]
        for contract_type in contract_types:
            if re.search(r'\b' + re.escape(contract_type) + r'\b', text, re.IGNORECASE):
                job_info["type_contrat"] = contract_type
                logger.debug(f"Type de contrat détecté par mot-clé: {contract_type}")
                break
    
    # Extraction des compétences requises - Patterns améliorés
    skills_patterns = [
        r"(?:^|\n)[\s•]*Compétences[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Compétences requises[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Compétences techniques[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Qualifications[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Prérequis[\s:]*(.+?)(?:\n\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Savoir-faire[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Profil recherché[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Profil[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Environnement et outils[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Outils[\s:]*(.+?)(?:\n\n|$)"
    ]
    
    for pattern in skills_patterns:
        skills_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            # Extraction des compétences en les séparant par saut de ligne ou par des puces
            skills = re.split(r'[\n•,]', skills_text)
            # Filtrer les compétences vides
            extracted_skills = [skill.strip() for skill in skills if skill.strip()]
            job_info["competences"].extend(extracted_skills)
            logger.debug(f"Compétences extraites via pattern: {pattern}")
            logger.debug(f"Compétences: {extracted_skills}")
    
    # Extrait les compétences à partir des puces - et des sections spécifiques
    env_tools_match = re.search(r"Environnement et outils\s*(.+?)(?:\n\s*\n|\n\s*Profil|\n\s*$)", text, re.DOTALL)
    if env_tools_match:
        env_tools = env_tools_match.group(1)
        # Extraire les compétences à partir des lignes qui commencent par un tiret
        env_skills = re.findall(r"-\s*(.+?)(?:\.\n|\n|$)", env_tools)
        job_info["competences"].extend([skill.strip() for skill in env_skills if skill.strip()])
        logger.debug(f"Compétences extraites de 'Environnement et outils': {env_skills}")
    
    # Extraction des compétences à partir de la section "Profil recherché"
    profile_match = re.search(r"Profil recherché\s*(.+?)(?:\n\s*\n|\n\s*Avantages|\n\s*$)", text, re.DOTALL)
    if profile_match:
        profile = profile_match.group(1)
        # Extraire les compétences à partir des lignes qui commencent par un tiret
        profile_skills = re.findall(r"-\s*(.+?)(?:\.\n|\n|$)", profile)
        # Ajouter seulement les lignes qui semblent être des compétences (pas la formation ou l'expérience)
        for skill in profile_skills:
            skill = skill.strip()
            if skill and not re.search(r'\bans d\'expérience\b|\bformation\b|\bdiplôme\b|\bbac\b', skill, re.IGNORECASE):
                job_info["competences"].append(skill)
        logger.debug(f"Compétences extraites de 'Profil recherché': {profile_skills}")
    
    # Si aucune compétence n'a été trouvée, rechercher des technologies et compétences spécifiques
    if not job_info["competences"]:
        logger.debug("Recherche de compétences spécifiques...")
        # Compétences techniques générales
        tech_skills = [
            "JavaScript", "React", "Angular", "Vue.js", "Node.js", "Python", "Django", "Flask",
            "Java", "Spring", "Hibernate", "C#", ".NET", "PHP", "Laravel", "Symfony",
            "Ruby", "Rails", "Go", "Rust", "Kotlin", "Swift", "SQL", "MySQL", "PostgreSQL",
            "MongoDB", "Redis", "Elasticsearch", "GraphQL", "REST", "SOAP", "HTML", "CSS",
            "Sass", "Less", "Bootstrap", "Tailwind", "Material-UI", "AWS", "Azure", "GCP",
            "Docker", "Kubernetes", "Jenkins", "GitHub Actions", "GitLab CI", "Git", "SVN",
            "Jira", "Confluence", "Agile", "Scrum", "Kanban", "TDD", "BDD", "DevOps", "CI/CD"
        ]
        
        # Compétences bureautiques et ERP
        business_skills = [
            "Excel", "Word", "PowerPoint", "Outlook", "SharePoint", "Office 365", "G Suite",
            "Google Workspace", "SAP", "Oracle", "PeopleSoft", "Salesforce", "Microsoft Dynamics",
            "Sage", "Cegid", "Talend", "Power BI", "Tableau", "QlikView", "Looker"
        ]
        
        # Compétences soft
        soft_skills = [
            "Communication", "Travail en équipe", "Gestion de projet", "Organisation", "Rigueur",
            "Autonomie", "Adaptabilité", "Polyvalence", "Réactivité", "Créativité", "Analyse",
            "Synthèse", "Résolution de problèmes", "Leadership", "Négociation", "Relationnel",
            "Gestion du stress", "Gestion du temps", "Prise de décision"
        ]
        
        # Combiner toutes les compétences à rechercher
        all_skills = tech_skills + business_skills + soft_skills
        
        found_skills = []
        for skill in all_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        if found_skills:
            job_info["competences"] = found_skills
            logger.debug(f"Compétences détectées par mots-clés: {found_skills}")
    
    # Déduplication des compétences
    if job_info["competences"]:
        job_info["competences"] = list(dict.fromkeys(job_info["competences"]))
    
    # Extraction de l'expérience requise - Patterns améliorés
    exp_patterns = [
        r"(?:^|\n)[\s•]*Expérience[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Années d'expérience[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*([\d]+[\s]*ans d'expérience)(?:\n|$)",
        r"(?:^|\n)[\s•]*Expérience requise[\s:]*(.+?)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*(\d+\s+à\s+\d+\s+ans\s+d'expérience\s+[^\n\.]+)",
        r"(?:^|\n)[\s•]*-\s*(\d+\s+à\s+\d+\s+ans\s+d'expérience\s+[^\n\.]+)",
        r"Profil recherché.*?-\s*(\d+\s*à\s*\d+\s*ans\s*d'expérience[^\n\.]*)"
    ]
    
    for pattern in exp_patterns:
        exp_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            job_info["experience"] = exp_match.group(1).strip()
            logger.debug(f"Expérience détectée: {job_info['experience']}")
            break
    
    # Extraction de la formation requise - Patterns améliorés
    edu_patterns = [
        r"(?:^|\n)[\s•]*Formation[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Diplôme[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Niveau d'études[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Éducation[\s:]*(.+?)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*-\s*(Formation\s+Bac\s*\+\s*\d+[^\n\.]*)",
        r"(?:^|\n)[\s•]*-\s*(Bac\s*\+\s*\d+[^\n\.]*)",
        r"Profil recherché.*?-\s*(Formation[^\n\.]*)",
        r"Profil recherché.*?-\s*(Bac\s*\+\s*\d+[^\n\.]*)"
    ]
    
    for pattern in edu_patterns:
        edu_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if edu_match:
            job_info["formation"] = edu_match.group(1).strip()
            logger.debug(f"Formation détectée: {job_info['formation']}")
            break
    
    # Extraction du salaire - Patterns améliorés
    salary_patterns = [
        r"(?:^|\n)[\s•]*Salaire[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Rémunération[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Package[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*\€[\s]*(.+?)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Salaire annuel[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Salaire mensuel[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*(\d+[\s-]*[kK€]+)",  # Format: 30k€, 30-35k€
        r"(?:^|\n)[\s•]*(\d+[\s-]+à[\s-]+\d+[kK€]+)",  # Format: 30 à 35k€
        r"(?:^|\n)[\s•]*(\d+[kK€]+-\d+[kK€]+)"  # Format: 30k€-35k€
    ]
    
    for pattern in salary_patterns:
        salary_match = re.search(pattern, text, re.IGNORECASE)
        if salary_match:
            job_info["salaire"] = salary_match.group(1).strip()
            logger.debug(f"Salaire détecté: {job_info['salaire']}")
            break
    
    # Extraction des avantages si présents
    advantages_match = re.search(r"Avantages\s*:?\s*(.+?)(?:\n\s*\n|$)", text, re.IGNORECASE | re.DOTALL)
    if advantages_match:
        advantages = advantages_match.group(1).strip()
        # Ajouter les avantages à la description si aucune n'est présente
        if not job_info["description"]:
            job_info["description"] = "Avantages : " + advantages
        else:
            job_info["description"] += "\n\nAvantages : " + advantages
        logger.debug(f"Avantages détectés: {advantages}")
    
    # Extraction de la description du poste - Patterns améliorés
    desc_patterns = [
        r"(?:^|\n)[\s•]*Description[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Description du poste[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Missions[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Responsabilités[\s:]*(.+?)(?:\n\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Missions principales[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Tâches[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*Activités[\s:]*(.+?)(?:\n\n|$)",
        r"(?:^|\n)[\s•]*principales\s*(.+?)(?:\n\s*\n|Environnement et outils|Profil recherché|$)",
        r"(?:^|\n)[\s•]*Principales activités[\s:]*(.+?)(?:\n\n|$)"
    ]
    
    for pattern in desc_patterns:
        desc_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if desc_match:
            job_info["description"] = desc_match.group(1).strip()
            logger.debug(f"Description détectée via pattern: {pattern}")
            logger.debug(f"Description (tronquée): {job_info['description'][:100]}...")
            break
    
    # Si aucune description n'a été trouvée, tenter une extraction plus générale
    if not job_info["description"]:
        logger.debug("Aucune description détectée via patterns, tentative d'extraction générale...")
        # Prendre les premiers paragraphes du texte comme description
        paragraphs = re.split(r'\n\n+', text)
        if len(paragraphs) > 1:
            # Ignorer le premier paragraphe qui contient souvent le titre
            job_info["description"] = " ".join(paragraphs[1:3])
            logger.debug(f"Description extraite des premiers paragraphes: {job_info['description'][:100]}...")
    
    # Extraire la date de publication si présente
    date_patterns = [
        r"(?:^|\n)[\s•]*Date[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Publié le[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Date de publication[\s:]*(.+?)(?:\n|$)",
        # Nouveaux patterns
        r"(?:^|\n)[\s•]*Mise en ligne[\s:]*(.+?)(?:\n|$)",
        r"(?:^|\n)[\s•]*Parue le[\s:]*(.+?)(?:\n|$)"
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            job_info["date_publication"] = date_match.group(1).strip()
            logger.debug(f"Date de publication détectée: {job_info['date_publication']}")
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
                "parser_version": "1.1.0"  # Version incrémentée
            },
            "job_info": job_info,
            "raw_text": text  # Ajout du texte brut pour faciliter le débogage
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
    parser.add_argument('--debug', '-d', action='store_true', help='Activer le mode débogage (très verbeux)')
    
    args = parser.parse_args()
    
    # Configuration du niveau de log en fonction des options
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    
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
        
        # Supprimer le texte brut du résultat avant de sauvegarder (pour éviter un fichier trop volumineux)
        result_to_save = result.copy()
        result_to_save.pop('raw_text', None)
        
        # Définir le nom du fichier de sortie
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = os.path.basename(args.pdf_path)
            output_file = f"job-parsing-result-{timestamp}-{filename}.json"
        
        # Sauvegarder le résultat dans un fichier JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_to_save, f, ensure_ascii=False, indent=2)
        
        # Afficher un résumé des informations extraites
        job_info = result["job_info"]
        print("\n--- Résultat du parsing ---")
        print(f"Titre du poste: {job_info.get('titre_poste', 'Non détecté')}")
        print(f"Entreprise: {job_info.get('entreprise', 'Non détectée')}")
        
        if job_info.get('localisation'):
            print(f"Localisation: {job_info.get('localisation')}")
        
        if job_info.get('type_contrat'):
            print(f"Type de contrat: {job_info.get('type_contrat')}")
        
        if job_info.get('formation'):
            print(f"Formation: {job_info.get('formation')}")
        
        if job_info.get('experience'):
            print(f"Expérience: {job_info.get('experience')}")
            
        if job_info.get('salaire'):
            print(f"Salaire: {job_info.get('salaire')}")
        
        if job_info.get('competences'):
            print(f"Compétences: {', '.join(job_info.get('competences'))}")
        else:
            print("Compétences: Non détectées")
        
        
        print(f"\nRésultat complet sauvegardé dans: {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
