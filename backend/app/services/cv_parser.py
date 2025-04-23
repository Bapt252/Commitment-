import os
import tempfile
from typing import Dict, Any, Optional

import docx
import PyPDF2
from fastapi import UploadFile

from app.models.cv import CV, CVSkill, CVExperience, CVEducation


class CVParserService:
    async def parse_cv(self, file: UploadFile) -> CV:
        """
        Parse a CV from a PDF or DOCX file
        """
        content = await self._extract_content(file)
        return self._analyze_content(content)

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
        Ceci est une version simplifiée à des fins de démonstration.
        """
        # Implémentation basique
        lines = content.split('\n')
        
        # Extraction des informations de base (approche naïve)
        name = lines[0] if lines else "Unknown"
        
        # Extraction de l'email (approche basique)
        email = None
        for line in lines:
            if '@' in line and '.' in line:
                words = line.split()
                for word in words:
                    if '@' in word and '.' in word:
                        email = word
                        break
                if email:
                    break
        
        # Extraction du téléphone (approche basique)
        phone = None
        for line in lines:
            # Recherche simple des motifs de numéros de téléphone
            if any(char.isdigit() for char in line):
                digits = ''.join(char for char in line if char.isdigit() or char in '+-.()')
                if len(digits) >= 10:
                    phone = digits
                    break
        
        # Extraction des compétences et logiciels
        skills = []
        softwares = []
        
        # Liste de mots-clés de logiciels courants
        software_keywords = [
            "python", "java", "javascript", "c++", "c#", "ruby", "php",
            "excel", "word", "powerpoint", "photoshop", "illustrator",
            "autocad", "matlab", "r", "tableau", "power bi", "sql",
            "mongodb", "oracle", "mysql", "postgresql", "git", "docker",
            "kubernetes", "aws", "azure", "gcp", "jenkins", "jira"
        ]
        
        # Extraction simple des compétences
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in [
                "skills", "compétences", "technologies", "langages", "outils"
            ]):
                # Prendre les lignes suivantes comme compétences
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and not any(heading in lines[j].lower() for heading in [
                        "experience", "education", "formation", "expérience"
                    ]):
                        skill_text = lines[j].strip()
                        skills.append(CVSkill(name=skill_text))
                        
                        # Vérifier si cette compétence est un logiciel
                        for software in software_keywords:
                            if software in skill_text.lower():
                                softwares.append(software)
        
        # Extraction du poste (approche simple)
        position = None
        for i, line in enumerate(lines):
            if i > 0 and i < 5:  # Généralement dans les premières lignes
                if any(title in line.lower() for title in [
                    "developer", "engineer", "consultant", "analyst", 
                    "manager", "director", "développeur", "ingénieur", 
                    "analyste", "chef de projet"
                ]):
                    position = line.strip()
                    break
        
        # Extraction des expériences (approche basique)
        experiences = []
        in_experience_section = False
        current_experience = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if any(keyword in line.lower() for keyword in ["expérience", "experience", "emploi", "parcours professionnel"]):
                in_experience_section = True
                continue
                
            if in_experience_section:
                if any(keyword in line.lower() for keyword in ["éducation", "education", "formation", "diplôme"]):
                    in_experience_section = False
                    continue
                    
                # Détection simple d'une nouvelle expérience (date + nom d'entreprise)
                if any(char.isdigit() for char in line) and len(line) < 100:
                    if current_experience:
                        experiences.append(current_experience)
                    
                    parts = line.split('-', 1)
                    company = parts[1].strip() if len(parts) > 1 else line
                    
                    current_experience = CVExperience(
                        title="", 
                        company=company,
                        description=""
                    )
                elif current_experience:
                    if not current_experience.title:
                        current_experience.title = line
                    else:
                        current_experience.description += line + " "
        
        # Ajouter la dernière expérience
        if current_experience:
            experiences.append(current_experience)
        
        # Créer l'objet CV
        return CV(
            name=name,
            email=email,
            phone=phone,
            position=position,
            skills=skills,
            softwares=softwares,
            experiences=experiences,
            education=[]  # L'extraction de l'éducation serait similaire à celle des expériences
        )


cv_parser_service = CVParserService()
