import os
import tempfile
from typing import Dict, Any, Optional
import logging

import docx
import PyPDF2
from fastapi import UploadFile

from app.models.cv import CV, CVSkill, CVExperience, CVEducation

# Configurez le logger pour le débogage
logger = logging.getLogger(__name__)

class CVParserService:
    async def parse_cv(self, file: UploadFile) -> CV:
        """
        Parse a CV from a PDF or DOCX file
        """
        content = await self._extract_content(file)
        parsed_data = self._analyze_content(content)
        
        # Enregistrez les données analysées pour le débogage
        logger.debug(f"Données CV analysées: {parsed_data}")
        
        return parsed_data

    async def _extract_content(self, file: UploadFile) -> str:
        """
        Extract text content from a PDF or DOCX file
        """
        temp_file_path = None
        try:
            # Save the file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                content = await file.read()
                temp_file.write(content)

            file_extension = os.path.splitext(file.filename)[1].lower()

            if file_extension == '.pdf':
                return self._parse_pdf(temp_file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._parse_docx(temp_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def _parse_pdf(self, file_path: str) -> str:
        """
        Parse text from a PDF file
        """
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text

    def _parse_docx(self, file_path: str) -> str:
        """
        Parse text from a DOCX file
        """
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _analyze_content(self, content: str) -> CV:
        """
        Analyze the extracted text content to extract structured CV information
        
        Note: Dans un scénario réel, cette méthode serait beaucoup plus sophistiquée,
        potentiellement en utilisant NLP ou des modèles ML pour extraire précisément les informations.
        Cette version a été améliorée pour une meilleure détection.
        """
        # Implémentation améliorée
        lines = content.split('\n')
        
        # Extraction des informations de base
        name = self._extract_name(lines)
        email = self._extract_email(lines)
        phone = self._extract_phone(lines)
        
        # Extraction du poste (approche améliorée)
        position = self._extract_position(lines)
        
        # Extraction des compétences
        skills = self._extract_skills(content)
        
        # Extraction des logiciels
        softwares = self._extract_softwares(content)
        
        # Extraction de l'expérience
        experiences = self._extract_experiences(content)
        
        # Extraction de l'éducation
        education = self._extract_education(content)
        
        # Création de l'objet CV avec des données structurées
        return CV(
            name=name,
            email=email,
            phone=phone,
            position=position,
            summary=self._extract_summary(content),
            skills=skills,
            softwares=softwares,
            experiences=experiences,
            education=education
        )
    
    def _extract_name(self, lines):
        """Extraction améliorée du nom"""
        if not lines:
            return "Non détecté"
        
        # Prendre les premières lignes non vides pour le nom
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 3 and len(line) < 40:
                # Vérifier si c'est probablement un nom (pas d'adresse email, pas de numéro)
                if '@' not in line and not any(char.isdigit() for char in line):
                    return line
        
        return "Non détecté"
    
    def _extract_email(self, lines):
        """Extraction améliorée de l'email"""
        for line in lines:
            if '@' in line and '.' in line:
                words = line.split()
                for word in words:
                    if '@' in word and '.' in word:
                        # Nettoyer l'email
                        email = word.strip('.,;:()"\'<>')
                        return email
        return None
    
    def _extract_phone(self, lines):
        """Extraction améliorée du téléphone"""
        for line in lines:
            # Recherche simple des motifs de numéros de téléphone
            if any(char.isdigit() for char in line):
                # Rechercher des motifs comme 06 12 34 56 78 ou +33 6 12 34 56 78
                digits = ''.join(char for char in line if char.isdigit() or char in '+-.()')
                if len(digits) >= 10:
                    return line.strip()
        return None
    
    def _extract_position(self, lines):
        """Extraction améliorée du poste"""
        for i, line in enumerate(lines):
            if i > 0 and i < 10:  # Généralement dans les premières lignes après le nom
                line = line.strip().lower()
                if any(title in line for title in [
                    "developer", "engineer", "consultant", "analyst", 
                    "manager", "director", "développeur", "ingénieur", 
                    "analyste", "chef de projet", "comptable", "auditeur",
                    "contrôleur", "financier"
                ]):
                    return lines[i].strip()
        return None
    
    def _extract_summary(self, content):
        """Extraction simple du résumé"""
        # Recherche de sections potentielles de résumé
        summary_markers = ["profil", "résumé", "à propos", "présentation", "summary", "profile", "about me"]
        
        lines = content.lower().split('\n')
        for i, line in enumerate(lines):
            if any(marker in line for marker in summary_markers) and i < len(lines) - 1:
                # Prendre les 3 lignes suivantes comme résumé
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and len(lines[j]) > 10:
                        summary_lines.append(lines[j])
                
                if summary_lines:
                    return " ".join(summary_lines)
        
        return None
    
    def _extract_skills(self, content):
        """Extraction améliorée des compétences"""
        # Liste de compétences communes
        common_skills = [
            "python", "java", "javascript", "react", "angular", "vue", 
            "node.js", "c++", "c#", ".net", "php", "ruby", "go", "sql",
            "nosql", "mongodb", "mysql", "postgresql", "oracle", "azure",
            "aws", "gcp", "docker", "kubernetes", "jenkins", "git",
            "agile", "scrum", "kanban", "jira", "confluence", "excel",
            "word", "powerpoint", "comptabilité", "fiscalité", "audit",
            "contrôle de gestion", "finance", "saas", "erp", "crm", 
            "communication", "management", "leadership", "marketing"
        ]
        
        skills = []
        content_lower = content.lower()
        
        # Chercher des compétences communes
        for skill in common_skills:
            if skill in content_lower:
                skills.append(CVSkill(name=skill.capitalize()))
        
        # Recherche de sections de compétences
        skill_sections = ["compétences", "skills", "expertise", "technologies", "tech stack"]
        
        lines = content_lower.split('\n')
        in_skills_section = False
        
        for i, line in enumerate(lines):
            # Détection de la section compétences
            if any(section in line for section in skill_sections):
                in_skills_section = True
                continue
            
            if in_skills_section:
                # Fin de la section si on rencontre une autre section
                if any(marker in line for marker in ["expérience", "experience", "formation", "education", "projets"]):
                    in_skills_section = False
                    continue
                
                # Analyse de la ligne pour des compétences
                words = line.strip().split(',')
                if not words:
                    words = line.strip().split()
                
                for word in words:
                    word = word.strip('•-–—*,:;.')
                    if word and len(word) > 2 and len(word) < 30 and not any(s.name.lower() == word.lower() for s in skills):
                        skills.append(CVSkill(name=word.capitalize()))
        
        return skills
    
    def _extract_softwares(self, content):
        """Extraction des logiciels"""
        common_softwares = [
            "sap", "oracle", "sage", "cegid", "microsoft office", "excel",
            "word", "powerpoint", "access", "dynamics", "quickbooks", 
            "adobe", "photoshop", "illustrator", "indesign", "autocad",
            "solidworks", "sketch", "figma", "xd", "jira", "trello",
            "asana", "slack", "teams", "zoom", "google workspace",
            "windows", "mac os", "linux", "unix", "salesforce"
        ]
        
        softwares = []
        content_lower = content.lower()
        
        for software in common_softwares:
            if software in content_lower:
                softwares.append(software.title())
        
        return softwares
    
    def _extract_experiences(self, content):
        """Extraction améliorée des expériences professionnelles"""
        experiences = []
        lines = content.split('\n')
        
        # Recherche de sections d'expérience
        exp_sections = ["expérience", "experience", "parcours professionnel", "emploi"]
        
        in_experience_section = False
        current_experience = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Détection de la section d'expérience
            if not in_experience_section and any(section in line.lower() for section in exp_sections):
                in_experience_section = True
                continue
            
            if in_experience_section:
                # Fin de la section si on rencontre une autre section
                if any(section in line.lower() for section in ["formation", "education", "compétences", "skills"]):
                    in_experience_section = False
                    
                    # Ajouter la dernière expérience
                    if current_experience and current_experience.company:
                        experiences.append(current_experience)
                        current_experience = None
                    
                    continue
                
                # Détection d'une nouvelle expérience
                if self._looks_like_new_experience(line):
                    # Ajouter l'expérience précédente si elle existe
                    if current_experience and current_experience.company:
                        experiences.append(current_experience)
                    
                    # Initialiser une nouvelle expérience
                    current_experience = CVExperience(
                        title="",
                        company=self._extract_company_from_line(line),
                        description=""
                    )
                    
                    # Extraire les dates si possible
                    dates = self._extract_dates_from_line(line)
                    if dates:
                        current_experience.start_date = dates[0]
                        if len(dates) > 1:
                            current_experience.end_date = dates[1]
                
                # Ajouter du contenu à l'expérience courante
                elif current_experience:
                    if not current_experience.title and len(line) < 100:
                        current_experience.title = line
                    else:
                        current_experience.description += line + " "
        
        # Ajouter la dernière expérience si nécessaire
        if current_experience and current_experience.company:
            experiences.append(current_experience)
        
        return experiences
    
    def _looks_like_new_experience(self, line):
        """Vérifie si une ligne semble être le début d'une nouvelle expérience"""
        # Recherche de dates et noms d'entreprise
        has_date = any(str(year) in line for year in range(2000, 2025))
        has_company_marker = any(marker in line.lower() for marker in ["chez ", "at ", "pour ", "for ", "inc", "ltd", "sarl", "sas", "sa", "gmbh"])
        has_date_separator = any(separator in line for separator in ["-", "–", "—", "to", "jusqu'à", "present", "aujourd'hui"])
        
        return has_date and (has_company_marker or has_date_separator)
    
    def _extract_company_from_line(self, line):
        """Extrait le nom de l'entreprise d'une ligne"""
        # Méthode simplifiée - dans un cas réel, utiliser NLP
        parts = line.split('-', 1)
        if len(parts) > 1:
            return parts[1].strip()
        
        parts = line.split('|', 1)
        if len(parts) > 1:
            return parts[1].strip()
        
        # Prendre la dernière partie de la ligne si contient une date
        if any(str(year) in line for year in range(2000, 2025)):
            # Supprimer la partie date
            for year in range(2000, 2025):
                if str(year) in line:
                    parts = line.split(str(year), 1)
                    if len(parts) > 1:
                        return parts[1].strip()
        
        return line
    
    def _extract_dates_from_line(self, line):
        """Extrait les dates d'une ligne"""
        dates = []
        
        # Recherche des années
        for year in range(2000, 2025):
            if str(year) in line:
                dates.append(str(year))
        
        # Recherche de termes comme "présent" ou "aujourd'hui"
        if any(term in line.lower() for term in ["present", "now", "aujourd'hui", "actuel", "en cours"]):
            dates.append("Présent")
        
        return dates
    
    def _extract_education(self, content):
        """Extraction de l'éducation"""
        education = []
        lines = content.split('\n')
        
        # Recherche de sections d'éducation
        edu_sections = ["formation", "education", "études", "diplômes", "scolarité"]
        
        in_education_section = False
        current_education = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Détection de la section d'éducation
            if not in_education_section and any(section in line.lower() for section in edu_sections):
                in_education_section = True
                continue
            
            if in_education_section:
                # Fin de la section si on rencontre une autre section
                if any(section in line.lower() for section in ["expérience", "experience", "compétences", "skills"]):
                    in_education_section = False
                    
                    # Ajouter la dernière formation
                    if current_education and current_education.institution:
                        education.append(current_education)
                        current_education = None
                    
                    continue
                
                # Détection d'une nouvelle formation
                if self._looks_like_new_education(line):
                    # Ajouter la formation précédente si elle existe
                    if current_education and current_education.institution:
                        education.append(current_education)
                    
                    # Initialiser une nouvelle formation
                    current_education = CVEducation(
                        degree="",
                        institution=self._extract_institution_from_line(line)
                    )
                    
                    # Extraire les dates si possible
                    dates = self._extract_dates_from_line(line)
                    if dates:
                        current_education.start_date = dates[0]
                        if len(dates) > 1:
                            current_education.end_date = dates[1]
                
                # Ajouter du contenu à la formation courante
                elif current_education:
                    if not current_education.degree and len(line) < 100:
                        current_education.degree = line
        
        # Ajouter la dernière formation si nécessaire
        if current_education and current_education.institution:
            education.append(current_education)
        
        return education
    
    def _looks_like_new_education(self, line):
        """Vérifie si une ligne semble être le début d'une nouvelle formation"""
        has_date = any(str(year) in line for year in range(2000, 2025))
        has_education_marker = any(marker in line.lower() for marker in 
                                ["école", "school", "université", "university", "institut", "institute", "diplôme", 
                                 "degree", "master", "bachelor", "licence", "doctoral", "doctorat", "phd", "mba"])
        
        return has_date or has_education_marker
    
    def _extract_institution_from_line(self, line):
        """Extrait le nom de l'institution d'une ligne"""
        # Méthode simplifiée - dans un cas réel, utiliser NLP
        for marker in ["école", "school", "université", "university", "institut", "institute"]:
            if marker in line.lower():
                parts = line.lower().split(marker, 1)
                if len(parts) > 1:
                    return (marker + parts[1]).capitalize()
        
        parts = line.split('-', 1)
        if len(parts) > 1:
            return parts[1].strip()
        
        return line


cv_parser_service = CVParserService()