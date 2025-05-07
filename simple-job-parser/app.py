from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import re
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configuration complète de CORS pour permettre l'accès depuis n'importe quelle origine
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": "*"}})

def extract_text_from_pdf(pdf_file):
    """Extraire le texte d'un fichier PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        logger.debug(f"Texte extrait du PDF (premiers 200 caractères): {text[:200]}...")
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
        raise

def extract_job_info(text):
    """Extraire les informations du poste à partir du texte"""
    # Dictionnaire pour stocker les informations extraites
    job_info = {
        "title": "",
        "skills": [],
        "contract_type": "",
        "location": "",
        "experience": "",
        "education": "",
        "salary": "",
        "company": ""
    }
    
    logger.debug("Début de l'extraction des informations")
    
    # Extraction du titre du poste
    logger.debug("Recherche du titre du poste")
    title_patterns = [
        r"(?:Poste\s*:\s*)(.*?)(?:\n|$)",
        r"(?:Titre\s*:\s*)(.*?)(?:\n|$)",
        r"(?:Intitulé du poste\s*:\s*)(.*?)(?:\n|$)"
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, text, re.IGNORECASE)
        if title_match:
            job_info["title"] = title_match.group(1).strip()
            logger.debug(f"Titre trouvé avec pattern {pattern}: {job_info['title']}")
            break
    
    if not job_info["title"]:
        # Prendre la première ligne non vide comme titre par défaut
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            job_info["title"] = lines[0]
            logger.debug(f"Titre par défaut (première ligne): {job_info['title']}")
    
    # Extraction du type de contrat
    logger.debug("Recherche du type de contrat")
    contract_patterns = [
        r"(?:Type de contrat|Contrat)\s*:\s*(.*?)(?:\n|$)",
        r"(?:CDI|CDD|Stage|Alternance|Freelance)",
        r"(?:Statut\s*:\s*)(.*?)(?:\n|$)"
    ]
    
    for pattern in contract_patterns:
        contract_match = re.search(pattern, text, re.IGNORECASE)
        if contract_match:
            job_info["contract_type"] = contract_match.group(0).strip() if pattern == r"(?:CDI|CDD|Stage|Alternance|Freelance)" else contract_match.group(1).strip()
            logger.debug(f"Type de contrat trouvé avec pattern {pattern}: {job_info['contract_type']}")
            break
    
    # Extraction de la localisation
    logger.debug("Recherche de la localisation")
    location_patterns = [
        r"(?:Lieu|Localisation|Location)\s*:\s*(.*?)(?:\n|$)",
        r"(?:Ville\s*:\s*)(.*?)(?:\n|$)",
        r"(?:Adresse\s*:\s*)(.*?)(?:\n|$)"
    ]
    
    for pattern in location_patterns:
        location_match = re.search(pattern, text, re.IGNORECASE)
        if location_match:
            job_info["location"] = location_match.group(1).strip()
            logger.debug(f"Localisation trouvée avec pattern {pattern}: {job_info['location']}")
            break
    
    # Extraction des compétences requises
    logger.debug("Recherche des compétences")
    skills_patterns = [
        r"(?:Compétences|Skills|Profil)\s*:\s*(.*?)(?:\n\n|\n[A-Z])",
        r"(?:Compétences techniques|Technical skills)\s*:\s*(.*?)(?:\n\n|\n[A-Z])",
        r"(?:Savoir-faire|Connaissances)\s*:\s*(.*?)(?:\n\n|\n[A-Z])"
    ]
    
    for pattern in skills_patterns:
        skills_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1)
            logger.debug(f"Texte des compétences trouvé: {skills_text}")
            
            # Diviser les compétences basées sur des puces ou des retours à la ligne
            skills = re.findall(r"[•\-\*]\s*(.*?)(?:\n|$)", skills_text)
            if skills:
                job_info["skills"] = [skill.strip() for skill in skills if skill.strip()]
                logger.debug(f"Compétences extraites (avec puces): {job_info['skills']}")
            else:
                # Si pas de puces, diviser par des virgules ou des points
                skills = re.split(r"[,.]", skills_text)
                job_info["skills"] = [skill.strip() for skill in skills if skill.strip()]
                logger.debug(f"Compétences extraites (avec virgules/points): {job_info['skills']}")
            
            break
    
    # Si aucune compétence trouvée, rechercher des technologies connues
    if not job_info["skills"]:
        logger.debug("Recherche de technologies connues dans le texte")
        known_techs = ["JavaScript", "React", "Node.js", "Python", "Java", "C++", "PHP", 
                      "HTML", "CSS", "MongoDB", "SQL", "Angular", "Vue", "TypeScript",
                      "Django", "Flask", "Spring", "Docker", "Kubernetes", "AWS", "Azure",
                      "Git", "Linux", "DevOps", "Agile", "Scrum"]
        
        found_techs = []
        for tech in known_techs:
            if re.search(r'\b' + re.escape(tech) + r'\b', text, re.IGNORECASE):
                found_techs.append(tech)
        
        if found_techs:
            job_info["skills"] = found_techs
            logger.debug(f"Technologies trouvées dans le texte: {found_techs}")
    
    # Extraction de l'expérience requise
    logger.debug("Recherche de l'expérience requise")
    experience_patterns = [
        r"(?:Expérience|Experience)\s*:\s*(.*?)(?:\n|$)",
        r"(\d+)[\s-]*an[s]?[\s-]*(d'expérience|d'exp|experience|expérience)",
        r"(?:Niveau d'expérience|Séniorité)\s*:\s*(.*?)(?:\n|$)"
    ]
    
    for pattern in experience_patterns:
        experience_match = re.search(pattern, text, re.IGNORECASE)
        if experience_match:
            if pattern == r"(\d+)[\s-]*an[s]?[\s-]*(d'expérience|d'exp|experience|expérience)":
                job_info["experience"] = f"{experience_match.group(1)} ans"
            else:
                job_info["experience"] = experience_match.group(1).strip()
            
            logger.debug(f"Expérience trouvée avec pattern {pattern}: {job_info['experience']}")
            break
    
    # Extraction du niveau d'éducation
    logger.debug("Recherche du niveau d'éducation")
    education_patterns = [
        r"(?:Formation|Éducation|Education|Diplôme)\s*:\s*(.*?)(?:\n|$)",
        r"(?:Niveau d'études|Formation requise)\s*:\s*(.*?)(?:\n|$)"
    ]
    
    for pattern in education_patterns:
        education_match = re.search(pattern, text, re.IGNORECASE)
        if education_match:
            job_info["education"] = education_match.group(1).strip()
            logger.debug(f"Éducation trouvée avec pattern {pattern}: {job_info['education']}")
            break
    
    # Extraction du salaire
    logger.debug("Recherche du salaire")
    salary_patterns = [
        r"(?:Salaire|Rémunération|Remuneration)\s*:\s*(.*?)(?:\n|$)",
        r"(\d+[\s-]*[k€]?€|\d+[\s-]*[k]?[\s-]*euros)"
    ]
    
    for pattern in salary_patterns:
        salary_match = re.search(pattern, text, re.IGNORECASE)
        if salary_match:
            if pattern == r"(\d+[\s-]*[k€]?€|\d+[\s-]*[k]?[\s-]*euros)":
                job_info["salary"] = salary_match.group(1)
            else:
                job_info["salary"] = salary_match.group(1).strip()
            
            logger.debug(f"Salaire trouvé avec pattern {pattern}: {job_info['salary']}")
            break
    
    # Extraction du nom de l'entreprise
    logger.debug("Recherche du nom de l'entreprise")
    company_patterns = [
        r"(?:Entreprise|Société|Company)\s*:\s*(.*?)(?:\n|$)",
        r"(?:Recruteur|Employeur)\s*:\s*(.*?)(?:\n|$)"
    ]
    
    for pattern in company_patterns:
        company_match = re.search(pattern, text, re.IGNORECASE)
        if company_match:
            job_info["company"] = company_match.group(1).strip()
            logger.debug(f"Entreprise trouvée avec pattern {pattern}: {job_info['company']}")
            break
    
    logger.debug(f"Informations extraites: {job_info}")
    return job_info

@app.route('/api/parse-job', methods=['POST'])
def parse_job():
    """Endpoint pour analyser un fichier PDF de fiche de poste"""
    logger.info("Requête reçue sur /api/parse-job")
    
    # Vérifier si un fichier a été envoyé
    if 'file' not in request.files:
        logger.warning("Aucun fichier n'a été envoyé")
        return jsonify({"error": "Aucun fichier n'a été envoyé"}), 400
    
    file = request.files['file']
    logger.info(f"Fichier reçu: {file.filename}")
    
    # Vérifier si le fichier est un PDF
    if file.filename == '' or not file.filename.endswith('.pdf'):
        logger.warning(f"Type de fichier invalide: {file.filename}")
        return jsonify({"error": "Le fichier doit être un PDF"}), 400
    
    try:
        # Extraire le texte du PDF
        logger.info("Extraction du texte du PDF...")
        text = extract_text_from_pdf(file)
        
        # Analyser le texte pour extraire les informations
        logger.info("Analyse du texte pour extraire les informations...")
        job_info = extract_job_info(text)
        
        logger.info(f"Résultat de l'analyse: {job_info}")
        return jsonify(job_info)
    except Exception as e:
        logger.error(f"Erreur lors du traitement du PDF: {str(e)}")
        return jsonify({"error": f"Erreur lors du traitement du PDF: {str(e)}"}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint pour vérifier que l'API est en ligne"""
    logger.info("Requête GET reçue sur /api/status")
    return jsonify({"status": "ok", "message": "API en ligne"})

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé"""
    logger.info("Vérification de santé")
    return jsonify({"status": "healthy"})

# Gérer les requêtes OPTIONS pour le CORS
@app.route('/api/parse-job', methods=['OPTIONS'])
def options_parse_job():
    logger.info("Requête OPTIONS reçue sur /api/parse-job")
    return "", 200

if __name__ == '__main__':
    logger.info("Démarrage du serveur sur le port 5054...")
    app.run(host='0.0.0.0', port=5054, debug=True)
