import re
import spacy
from typing import Dict, List, Tuple, Any, Optional, Union
from app.nlp.document_classifier import preprocess_document

class CVExtractor:
    def __init__(self):
        # Chargement du modèle SpaCy
        try:
            self.nlp = spacy.load("fr_core_news_lg")
        except OSError:
            spacy.cli.download("fr_core_news_lg")
            self.nlp = spacy.load("fr_core_news_lg")
        
        self.extractors = {
            "nom": self.extract_name,
            "contact": self.extract_contact,
            "titre": self.extract_title,
            "competences": self.extract_skills,
            "formation": self.extract_education,
            "experience": self.extract_experience,
            "langues": self.extract_languages
        }
    
    def parse_cv(self, text: str) -> Dict[str, Any]:
        """
        Parse un CV et extrait les informations pertinentes
        
        Args:
            text: Le texte du CV à analyser
            
        Returns:
            Dict: Informations extraites avec scores de confiance
        """
        # Prétraitement du document
        processed = preprocess_document(text)
        
        # Découpage en sections (spécifique aux CV)
        sections = self._extract_sections(processed["text"])
        processed["sections"] = sections
        
        results = {}
        confidence = {}
        
        # Extraction de chaque champ
        for field, extractor in self.extractors.items():
            value, score = extractor(processed)
            results[field] = value
            confidence[field] = score
        
        # Calculer un score global
        global_score = self._calculate_confidence_scores(results)
        confidence.update(global_score)
        
        return {
            "extracted_data": results,
            "confidence_scores": confidence
        }
    
    def _extract_sections(self, text: str) -> Dict[str, List[str]]:
        """
        Découpe le CV en sections logiques
        
        Args:
            text: Le texte du CV
            
        Returns:
            Dict: Sections du CV
        """
        sections = {}
        current_section = "header"
        sections[current_section] = []
        
        # Patterns communs pour les titres de section dans un CV
        section_patterns = [
            (r'expériences?\s+professionnelles?', 'experience'),
            (r'formations?|éducations?|études', 'formation'),
            (r'compétences?\s+techniques?', 'competences'),
            (r'langues?', 'langues'),
            (r'projets?', 'projets'),
            (r'loisirs?|centres\s+d\'intérêts?', 'loisirs'),
            (r'coordonnées|contact', 'contact')
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Détection des titres de section
            is_section_header = False
            
            # 1. Vérifier si la ligne est en majuscules ou a une mise en forme de titre
            if re.match(r'^[A-Z\s]{3,30}[\s:]*$', line):
                # C'est probablement un titre de section
                is_section_header = True
                current_section = line.strip(':').lower()
                sections[current_section] = []
                continue
            
            # 2. Vérifier avec les patterns connus
            for pattern, section_name in section_patterns:
                if re.search(pattern, line.lower()):
                    is_section_header = True
                    current_section = section_name
                    sections[current_section] = []
                    break
            
            if not is_section_header:
                # Ajouter la ligne à la section courante
                sections[current_section].append(line)
        
        return sections
    
    def extract_name(self, processed: Dict[str, Any]) -> Tuple[str, float]:
        """
        Extrait le nom du candidat du CV
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (nom, score de confiance)
        """
        doc = processed["spacy_doc"]
        text = processed["text"]
        
        # Stratégie 1: Chercher dans l'en-tête
        if "header" in processed["sections"]:
            header_text = " ".join(processed["sections"]["header"])
            
            # Utiliser spaCy pour trouver des entités de type PERSON
            header_doc = self.nlp(header_text)
            for ent in header_doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text, 0.9
            
            # Si pas trouvé, prendre la première ligne non vide (souvent le nom)
            first_line = next((line for line in processed["sections"]["header"] if line.strip()), "")
            if first_line and len(first_line.split()) <= 4:  # Un nom a généralement 2-4 mots
                return first_line, 0.8
        
        # Stratégie 2: Chercher dans tout le document
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if persons:
            # Prendre la personne la plus mentionnée
            from collections import Counter
            person_counter = Counter(persons)
            most_common = person_counter.most_common(1)[0][0]
            return most_common, 0.7
        
        return "Non spécifié", 0.3
    
    def extract_contact(self, processed: Dict[str, Any]) -> Tuple[Dict[str, str], float]:
        """
        Extrait les informations de contact
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (dict de contacts, score de confiance)
        """
        text = processed["text"]
        
        contact_info = {}
        score = 0.5  # Score de base
        
        # Recherche d'email
        email_pattern = r'[\w.+-]+@[\w-]+\.[\w.-]+'
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            contact_info["email"] = email_matches[0]
            score += 0.2
        
        # Recherche de téléphone
        phone_patterns = [
            r'(?:\+33|0)\s*[1-9](?:[\s.-]*\d{2}){4}',  # Format français
            r'\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}'  # Format simple
        ]
        
        for pattern in phone_patterns:
            phone_matches = re.findall(pattern, text)
            if phone_matches:
                # Nettoyer le numéro de téléphone
                phone = re.sub(r'[\s.-]', '', phone_matches[0])
                contact_info["telephone"] = phone
                score += 0.15
                break
        
        # Recherche d'adresse
        # C'est plus complexe, mais on peut chercher des patterns comme des codes postaux
        postal_code_pattern = r'\b\d{5}\b'
        postal_codes = re.findall(postal_code_pattern, text)
        
        if postal_codes:
            # Chercher des lignes contenant ces codes postaux
            lines = text.split('\n')
            for line in lines:
                if any(code in line for code in postal_codes):
                    contact_info["adresse"] = line.strip()
                    score += 0.15
                    break
        
        # Recherche de LinkedIn ou autres réseaux
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact_info["linkedin"] = linkedin_matches[0]
            score += 0.1
        
        # Ajuster le score final selon le nombre d'infos trouvées
        if not contact_info:
            return {"email": "Non spécifié"}, 0.3
        
        return contact_info, min(0.95, score)
    
    def extract_title(self, processed: Dict[str, Any]) -> Tuple[str, float]:
        """
        Extrait le titre professionnel du candidat
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (titre, score de confiance)
        """
        doc = processed["spacy_doc"]
        text = processed["text"]
        
        # Stratégie 1: Chercher dans l'en-tête après le nom
        if "header" in processed["sections"] and len(processed["sections"]["header"]) > 1:
            # Éviter la première ligne (probablement le nom)
            for line in processed["sections"]["header"][1:3]:  # Regarder les 2-3 premières lignes
                # Les titres ont généralement moins de 10 mots
                if 2 <= len(line.split()) <= 10:
                    # Vérifier si contient des mots-clés de poste
                    job_keywords = ["développeur", "ingénieur", "technicien", "chef", "directeur", "consultant"]
                    if any(keyword in line.lower() for keyword in job_keywords):
                        return line, 0.9
                    else:
                        return line, 0.7
        
        # Stratégie 2: Chercher dans une section "profil" ou "à propos"
        profile_sections = ["profil", "about", "à propos", "présentation"]
        for section in profile_sections:
            if section in processed["sections"] and processed["sections"][section]:
                first_line = processed["sections"][section][0]
                if 2 <= len(first_line.split()) <= 10:
                    return first_line, 0.8
        
        # Stratégie 3: Utiliser spaCy pour trouver des entités de type PROFESSION
        for ent in doc.ents:
            if ent.label_ == "PROFESSION":
                return ent.text, 0.75
        
        return "Non spécifié", 0.3
    
    def extract_skills(self, processed: Dict[str, Any]) -> Tuple[List[str], float]:
        """
        Extrait les compétences techniques
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (liste de compétences, score de confiance)
        """
        text = processed["text"]
        
        # Liste des compétences techniques courantes à rechercher
        tech_skills = [
            "python", "java", "javascript", "c++", "sql", "react", "angular", "vue", 
            "node.js", "django", "flask", "spring", "aws", "azure", "docker", "kubernetes",
            "tensorflow", "pytorch", "nlp", "machine learning", "git", "devops",
            "php", "html", "css", "ruby", "c#", ".net", "swift", "kotlin", "android",
            "ios", "react native", "flutter", "wordpress", "photoshop", "illustrator",
            "excel", "powerpoint", "word", "sap", "salesforce", "jira", "scrum", "agile"
        ]
        
        # Chercher dans la section compétences si elle existe
        skills = []
        score = 0.5  # Score de base
        
        if "competences" in processed["sections"]:
            comp_text = " ".join(processed["sections"]["competences"])
            
            # Chercher les éléments de liste (•, -, *)
            list_items = re.findall(r'[•\-\*]\s*([\w\s\+\#\./]+)', comp_text)
            for item in list_items:
                skills.append(item.strip())
            
            # Si on a trouvé des éléments de liste, augmenter le score
            if list_items:
                score = 0.8
        
        # Rechercher les compétences techniques dans tout le texte
        found_skills = []
        for skill in tech_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                found_skills.append(skill)
        
        # Combiner les résultats
        if found_skills and not skills:
            skills = found_skills
            score = 0.7
        elif found_skills:
            # Ajouter des compétences trouvées mais non présentes dans skills
            for skill in found_skills:
                if not any(skill.lower() in s.lower() for s in skills):
                    skills.append(skill)
            score = max(score, 0.75)
        
        # Nettoyer et dédupliquer
        clean_skills = []
        for skill in skills:
            skill = skill.strip().rstrip('.,;:')
            if skill and len(skill) > 1:
                if not any(skill.lower() == s.lower() for s in clean_skills):
                    clean_skills.append(skill)
        
        if not clean_skills:
            return ["Non spécifié"], 0.3
        
        return clean_skills, score
    
    def extract_education(self, processed: Dict[str, Any]) -> Tuple[List[Dict[str, str]], float]:
        """
        Extrait les informations de formation
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (liste de formations, score de confiance)
        """
        text = processed["text"]
        
        education_list = []
        score = 0.5  # Score de base
        
        # Chercher dans la section formation
        if "formation" in processed["sections"]:
            section_text = processed["sections"]["formation"]
            
            # Patterns pour les dates (pour séparer les entrées)
            date_patterns = [
                r'\b(\d{4})\s*[\-–—]\s*(\d{4}|présent|aujourd\'hui)\b',
                r'\b(\d{4})\b'
            ]
            
            # Patterns pour les diplômes
            degree_patterns = [
                r'\b(master|licence|bac\+\d|doctorat|thèse|ingénieur|diplôme)\b',
                r'\b(école|université|institut)\b'
            ]
            
            current_entry = {}
            
            for line in section_text:
                line = line.strip()
                if not line:
                    continue
                
                # Détection de nouvelle entrée par date
                new_entry = False
                for pattern in date_patterns:
                    date_match = re.search(pattern, line, re.IGNORECASE)
                    if date_match:
                        if current_entry and 'degree' in current_entry:
                            education_list.append(current_entry)
                        current_entry = {'period': date_match.group(0)}
                        new_entry = True
                        break
                
                if not new_entry:
                    # Recherche du diplôme et de l'établissement
                    for pattern in degree_patterns:
                        degree_match = re.search(pattern, line, re.IGNORECASE)
                        if degree_match:
                            if 'degree' not in current_entry:
                                current_entry['degree'] = line
                            else:
                                current_entry['institution'] = line
                            break
            
            # Ajouter la dernière entrée si elle existe
            if current_entry and 'degree' in current_entry:
                education_list.append(current_entry)
            
            # Ajuster le score en fonction du nombre d'entrées trouvées
            if education_list:
                score = min(0.9, 0.6 + len(education_list) * 0.1)
        
        if not education_list:
            # Chercher dans tout le texte
            # Patterns pour diplômes et établissements
            edu_patterns = [
                r'\b(master|licence|bac\+\d|doctorat|thèse|ingénieur|diplôme)\s+([^\.,;]+)',
                r'\b(école|université|institut)\s+([^\.,;]+)'
            ]
            
            for pattern in edu_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    education_list.append({
                        'degree': match.group(0)
                    })
            
            if education_list:
                score = 0.6
        
        if not education_list:
            return [{"degree": "Non spécifié"}], 0.3
        
        return education_list, score
    
    def extract_experience(self, processed: Dict[str, Any]) -> Tuple[List[Dict[str, str]], float]:
        """
        Extrait les expériences professionnelles
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (liste d'expériences, score de confiance)
        """
        text = processed["text"]
        
        experience_list = []
        score = 0.5  # Score de base
        
        # Chercher dans la section expérience
        if "experience" in processed["sections"]:
            section_text = processed["sections"]["experience"]
            
            # Patterns pour les dates (pour séparer les entrées)
            date_patterns = [
                r'\b(\d{4})\s*[\-–—]\s*(\d{4}|présent|aujourd\'hui)\b',
                r'\b(\d{2}/\d{2})\s*[\-–—]\s*(\d{2}/\d{2}|présent|aujourd\'hui)\b',
                r'\b(\w+ \d{4})\s*[\-–—]\s*(\w+ \d{4}|présent|aujourd\'hui)\b'
            ]
            
            current_entry = {}
            description_lines = []
            
            for line in section_text:
                line = line.strip()
                if not line:
                    continue
                
                # Détection de nouvelle entrée par date
                new_entry = False
                for pattern in date_patterns:
                    date_match = re.search(pattern, line, re.IGNORECASE)
                    if date_match:
                        # Sauvegarder l'entrée précédente
                        if current_entry and 'title' in current_entry:
                            if description_lines:
                                current_entry['description'] = '\n'.join(description_lines)
                            experience_list.append(current_entry)
                        
                        # Nouvelle entrée
                        current_entry = {'period': date_match.group(0)}
                        description_lines = []
                        new_entry = True
                        
                        # Chercher le titre et l'entreprise sur la même ligne
                        rest_of_line = line.replace(date_match.group(0), '').strip(' |,:-')
                        if rest_of_line:
                            current_entry['title'] = rest_of_line
                        
                        break
                
                if not new_entry:
                    # Si c'est la première ligne après la date, c'est probablement le titre
                    if 'period' in current_entry and 'title' not in current_entry:
                        current_entry['title'] = line
                    # Sinon c'est une ligne de description
                    elif 'title' in current_entry:
                        description_lines.append(line)
            
            # Ajouter la dernière entrée si elle existe
            if current_entry and 'title' in current_entry:
                if description_lines:
                    current_entry['description'] = '\n'.join(description_lines)
                experience_list.append(current_entry)
            
            # Ajuster le score en fonction du nombre d'entrées trouvées
            if experience_list:
                score = min(0.9, 0.6 + len(experience_list) * 0.1)
        
        if not experience_list:
            return [{"title": "Non spécifié"}], 0.3
        
        return experience_list, score
    
    def extract_languages(self, processed: Dict[str, Any]) -> Tuple[List[Dict[str, str]], float]:
        """
        Extrait les langues parlées
        
        Args:
            processed: Document prétraité
            
        Returns:
            Tuple: (liste de langues avec niveau, score de confiance)
        """
        text = processed["text"]
        
        languages = []
        score = 0.5  # Score de base
        
        # Liste des langues courantes
        common_languages = [
            "français", "anglais", "espagnol", "allemand", "italien",
            "portugais", "russe", "chinois", "japonais", "arabe"
        ]
        
        # Niveaux courants
        level_patterns = [
            r'\b(natif|maternel|bilingue|courant|intermédiaire|scolaire|notions|débutant|avancé|C2|C1|B2|B1|A2|A1)\b'
        ]
        
        # Chercher dans la section langues
        if "langues" in processed["sections"]:
            section_text = " ".join(processed["sections"]["langues"])
            
            for lang in common_languages:
                if re.search(r'\b' + re.escape(lang) + r'\b', section_text, re.IGNORECASE):
                    lang_entry = {"language": lang.capitalize()}
                    
                    # Chercher le niveau
                    for pattern in level_patterns:
                        level_matches = re.finditer(pattern, section_text, re.IGNORECASE)
                        for match in level_matches:
                            # Vérifier si le niveau est proche de la langue
                            lang_pos = section_text.lower().find(lang)
                            level_pos = match.start()
                            
                            if abs(lang_pos - level_pos) < 50:  # Si à moins de 50 caractères
                                lang_entry["level"] = match.group(0).capitalize()
                                break
                    
                    languages.append(lang_entry)
            
            score = 0.8
        
        # Si pas trouvé dans section dédiée, chercher dans tout le texte
        if not languages:
            for lang in common_languages:
                if re.search(r'\b' + re.escape(lang) + r'\b', text, re.IGNORECASE):
                    languages.append({"language": lang.capitalize()})
            
            if languages:
                score = 0.6
        
        if not languages:
            return [{"language": "Non spécifié"}], 0.3
        
        return languages, score
    
    def _calculate_confidence_scores(self, extracted_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule un score de confiance global pour l'extraction
        
        Args:
            extracted_data: Données extraites
            
        Returns:
            Dict: Score de confiance global
        """
        scores = {}
        
        # Calculer la complétude
        non_empty_fields = sum(1 for key, value in extracted_data.items() 
                               if value and value != "Non spécifié" and 
                               (not isinstance(value, list) or value[0] != "Non spécifié"))
        
        completeness = non_empty_fields / len(extracted_data)
        
        # Calculer la cohérence
        coherence = 1.0
        
        # Par exemple, vérifier si le titre correspond aux compétences
        if extracted_data.get("titre") and extracted_data.get("competences"):
            titre = extracted_data["titre"].lower()
            competences = [c.lower() for c in extracted_data["competences"]] \
                         if isinstance(extracted_data["competences"], list) else []
            
            # Vérifier s'il y a une correspondance
            title_skills_match = any(skill in titre for skill in competences)
            if not title_skills_match:
                coherence *= 0.9
        
        # Score global
        global_score = 0.6 * completeness + 0.4 * coherence
        scores["global"] = round(global_score, 2)
        
        return scores

# Fonction d'interface
def parse_cv(text: str) -> Dict[str, Any]:
    """
    Point d'entrée principal pour le parsing d'un CV
    
    Args:
        text: Texte du CV
        
    Returns:
        Dict: Informations extraites avec scores de confiance
    """
    extractor = CVExtractor()
    return extractor.parse_cv(text)