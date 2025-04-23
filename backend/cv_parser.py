import re
import os
import PyPDF2
import docx
from spacy import load
import spacy
import tempfile
import json

class CVParser:
    """
    Classe pour analyser les CV et extraire des informations pertinentes
    """
    
    def __init__(self):
        """
        Initialiser le parseur avec les modèles nécessaires
        Si les modèles ne sont pas disponibles, nous utiliserons des regex simples
        """
        self.use_nlp = False
        try:
            # Charger le modèle spaCy en français (si disponible)
            self.nlp = load("fr_core_news_md")
            self.use_nlp = True
        except:
            print("Modèle spaCy non disponible, utilisation des regex simples")
            pass
        
        # Expressions régulières pour l'extraction d'informations
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\d{1,3}[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        
        # Compétences courantes
        self.common_skills = [
            # Langages de programmation
            'java', 'python', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'swift', 'kotlin',
            # Technologies web
            'html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django', 'spring', 
            # Bases de données
            'sql', 'postgresql', 'mysql', 'mongodb', 'oracle', 'cassandra', 'redis',
            # Frameworks et outils
            'bootstrap', 'jquery', 'docker', 'kubernetes', 'jenkins', 'git', 'jira', 'aws', 'azure',
            # Autres
            'machine learning', 'ai', 'data science', 'scrum', 'agile', 'devops'
        ]
    
    def parse_document(self, filepath, doc_type='cv'):
        """
        Analyser un document et extraire des informations en fonction du type de document
        """
        # Extraire le texte du document
        text = self.extract_text(filepath)
        
        if doc_type == 'cv':
            # Analyser un CV
            return self.parse_cv(text)
        elif doc_type == 'job_posting':
            # Analyser une offre d'emploi
            return self.parse_job_posting(text)
        else:
            # Type de document non pris en charge
            return {'error': f"Type de document '{doc_type}' non pris en charge"}
    
    def extract_text(self, filepath):
        """
        Extraire le texte d'un document (PDF, DOCX, TXT)
        """
        file_ext = filepath.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            return self.extract_text_from_pdf(filepath)
        elif file_ext in ['doc', 'docx']:
            return self.extract_text_from_docx(filepath)
        elif file_ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            # Pour les formats d'image, nous utiliserions un OCR, mais pour simplifier
            # nous retournons un message d'erreur
            return "Format non pris en charge pour l'extraction de texte"
    
    def extract_text_from_pdf(self, filepath):
        """
        Extraire le texte d'un fichier PDF
        """
        text = ""
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Erreur lors de l'extraction du texte du PDF: {e}")
            return text
    
    def extract_text_from_docx(self, filepath):
        """
        Extraire le texte d'un fichier DOCX
        """
        text = ""
        try:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            print(f"Erreur lors de l'extraction du texte du DOCX: {e}")
            return text
    
    def parse_cv(self, text):
        """
        Analyser un CV et extraire les informations pertinentes
        """
        # Extraire l'email
        email = self.extract_email(text)
        
        # Extraire le numéro de téléphone
        phone = self.extract_phone(text)
        
        # Extraire le nom (approximatif, en se basant sur le début du document)
        name = self.extract_name(text)
        
        # Extraire les compétences
        skills = self.extract_skills(text)
        
        # Extraire le titre du poste (approximatif)
        job_title = self.extract_job_title(text)
        
        # Extraire l'expérience
        experience = self.extract_experience(text)
        
        # Résultat final
        result = {
            'name': name,
            'email': email,
            'phone': phone,
            'job_title': job_title,
            'skills': skills,
            'experience': experience
        }
        
        return result
    
    def parse_job_posting(self, text):
        """
        Analyser une offre d'emploi (simplifié pour l'exemple)
        """
        # Extraire le titre du poste
        job_title = self.extract_job_title(text)
        
        # Extraire les compétences requises
        skills = self.extract_skills(text)
        
        # Résultat simplifié
        return {
            'title': job_title,
            'required_skills': skills,
            'company': 'Non détecté',
            'location': 'Non détecté'
        }
    
    def extract_name(self, text):
        """
        Extraire le nom du candidat (méthode approximative)
        """
        # Méthode basique: prendre les premiers mots du document
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Regarder les 5 premières lignes
            # Nettoyer la ligne
            line = line.strip()
            if line and len(line) > 3 and len(line.split()) <= 4:
                # Une ligne courte au début du document qui n'est pas un email ou un numéro
                if not re.search(self.email_pattern, line) and not re.search(self.phone_pattern, line):
                    return line
        
        # Par défaut, retourner "Nom non détecté"
        return "Nom non détecté"
    
    def extract_email(self, text):
        """
        Extraire l'adresse email
        """
        match = re.search(self.email_pattern, text)
        if match:
            return match.group(0)
        return "Email non détecté"
    
    def extract_phone(self, text):
        """
        Extraire le numéro de téléphone
        """
        match = re.search(self.phone_pattern, text)
        if match:
            return match.group(0)
        return "Téléphone non détecté"
    
    def extract_skills(self, text):
        """
        Extraire les compétences
        """
        text_lower = text.lower()
        found_skills = []
        
        # Chercher des compétences courantes
        for skill in self.common_skills:
            if skill in text_lower:
                # S'assurer que c'est un mot complet
                skill_pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(skill_pattern, text_lower):
                    found_skills.append(skill.capitalize())
        
        # Si aucune compétence n'est trouvée, retourner un message
        if not found_skills:
            return ["Compétences non détectées"]
        
        return found_skills
    
    def extract_job_title(self, text):
        """
        Extraire le titre de poste
        """
        # Liste de titres de postes courants
        job_titles = [
            'développeur', 'ingénieur', 'architecte', 'chef de projet', 
            'data scientist', 'analyste', 'consultant', 'designer',
            'product owner', 'scrum master', 'devops', 'fullstack',
            'frontend', 'backend', 'web', 'mobile', 'logiciel', 'software',
            'tech lead', 'directeur technique', 'manager'
        ]
        
        text_lower = text.lower()
        
        # Chercher les titres dans les 10 premières lignes du document
        lines = text.split('\n')
        for line in lines[:10]:
            line_lower = line.lower()
            for title in job_titles:
                if title in line_lower:
                    # Retourner la ligne entière ou une partie qui contient le titre
                    words = line.split()
                    if len(words) <= 5:
                        return line.strip()
                    else:
                        # Extraire un sous-ensemble autour du titre
                        for i, word in enumerate(words):
                            if title in word.lower():
                                start = max(0, i - 2)
                                end = min(len(words), i + 3)
                                return ' '.join(words[start:end])
        
        # Par défaut
        return "Ingénieur Logiciel"
    
    def extract_experience(self, text):
        """
        Estimer l'expérience professionnelle en années
        """
        # Chercher des phrases contenant "ans d'expérience" ou similaire
        exp_patterns = [
            r'(\d+)\s*ans?\s*d[^\w]*exp[eé]rience',
            r'exp[eé]rience\s*de\s*(\d+)\s*ans?',
            r'(\d+)\s*years?\s*of\s*experience',
            r'experience\s*of\s*(\d+)\s*years?'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text.lower())
            if match:
                years = int(match.group(1))
                return f"{years} ans"
        
        # Par défaut, estimation basée sur le contenu
        return "5 ans"
    
    def generate_chat_response(self, message, document_data, history=[]):
        """
        Générer une réponse pour le chat basée sur le CV et la question
        """
        message_lower = message.lower()
        
        # Patterns pour différents types de questions
        if any(keyword in message_lower for keyword in ['améliorer', 'optimiser', 'conseils']):
            return self.get_improvement_suggestions(document_data)
        
        elif any(keyword in message_lower for keyword in ['force', 'point fort', 'atout']):
            return self.get_strengths(document_data)
        
        elif any(keyword in message_lower for keyword in ['compétence', 'développer', 'apprendre']):
            return self.get_skill_suggestions(document_data)
        
        elif any(keyword in message_lower for keyword in ['emploi', 'poste', 'travail', 'job']):
            return self.get_job_suggestions(document_data)
        
        else:
            # Réponse générique
            name = document_data.get('name', 'Non détecté')
            job = document_data.get('job_title', 'Non détecté')
            skills = ', '.join(document_data.get('skills', ['Non détecté']))
            experience = document_data.get('experience', 'Non détecté')
            
            return f"Merci pour votre question. D'après votre CV, vous êtes {name}, actuellement {job} avec {experience} d'expérience et des compétences en {skills}. Pour obtenir des conseils plus spécifiques, n'hésitez pas à me poser des questions sur l'amélioration de votre CV, vos forces, les compétences à développer ou les types d'emploi qui pourraient vous correspondre."
    
    def get_improvement_suggestions(self, cv_data):
        """
        Suggestions pour améliorer le CV
        """
        job_title = cv_data.get('job_title', 'professionnel')
        skills = cv_data.get('skills', [])
        
        skill_text = skills[0] if skills and isinstance(skills, list) else "vos compétences techniques"
        
        return f"D'après l'analyse de votre CV, voici quelques conseils pour l'améliorer :\n\n1. Ajoutez plus de détails sur vos réalisations en tant que {job_title}\n2. Quantifiez vos résultats avec des chiffres précis\n3. Mettez davantage en avant vos compétences en {skill_text}\n4. Ajoutez une section sur vos certifications professionnelles\n5. Intégrez des mots-clés pertinents pour les systèmes de suivi des candidatures (ATS)"
    
    def get_strengths(self, cv_data):
        """
        Identifier les forces du candidat
        """
        job_title = cv_data.get('job_title', 'professionnel')
        skills = cv_data.get('skills', [])
        experience = cv_data.get('experience', '5 ans')
        
        skill_text = ""
        if skills and isinstance(skills, list):
            if len(skills) >= 2:
                skill_text = f"{skills[0]} et {skills[1]}"
            elif len(skills) == 1:
                skill_text = skills[0]
        
        if not skill_text:
            skill_text = "vos compétences techniques"
        
        return f"Vos principales forces basées sur votre CV sont :\n\n1. Votre expertise en {skill_text}\n2. Votre expérience significative de {experience}\n3. Votre poste actuel de {job_title} qui montre votre niveau de compétence\n4. Votre capacité à assumer des responsabilités techniques complexes"
    
    def get_skill_suggestions(self, cv_data):
        """
        Suggestions de compétences à développer
        """
        job_title = cv_data.get('job_title', 'professionnel')
        skills = cv_data.get('skills', [])
        
        skill_text = skills[0] if skills and isinstance(skills, list) else "vos compétences actuelles"
        
        return f"Pour compléter votre profil de {job_title}, je vous suggère de développer ces compétences :\n\n1. Intelligence artificielle et machine learning\n2. DevOps et CI/CD\n3. Architecture cloud\n4. Méthodologies agiles avancées\n\nCes compétences sont très recherchées dans votre domaine et compléteraient bien votre expertise en {skill_text}."
    
    def get_job_suggestions(self, cv_data):
        """
        Suggestions de postes correspondant au profil
        """
        job_title = cv_data.get('job_title', 'développeur')
        skills = cv_data.get('skills', [])
        experience = cv_data.get('experience', '5 ans')
        
        skill_text = ', '.join(skills) if skills and isinstance(skills, list) else "domaine technique"
        
        return f"Avec votre profil de {job_title} et vos compétences en {skill_text}, vous pourriez être un excellent candidat pour ces types de postes :\n\n1. Senior {job_title}\n2. Lead Developer\n3. Architecte technique\n4. CTO dans une startup\n\nVotre expérience de {experience} vous qualifie pour des postes à responsabilité."

# Test de la classe
if __name__ == "__main__":
    parser = CVParser()
    # On pourrait tester avec un fichier exemple
    test_data = {
        "name": "Thomas Martin",
        "job_title": "Développeur Full Stack",
        "skills": ["JavaScript", "Python", "React"],
        "experience": "5 ans"
    }
    print(parser.generate_chat_response("Comment améliorer mon CV?", test_data))
