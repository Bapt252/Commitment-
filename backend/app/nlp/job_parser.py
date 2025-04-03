import re
import spacy
import torch
from typing import Dict, List, Tuple, Any, Optional, Union
from transformers import CamembertTokenizer, CamembertModel
from app.core.config import settings

# Chargement des modèles à l'initialisation
nlp = None
tokenizer = None
model = None

def load_models():
    """Charge les modèles NLP nécessaires"""
    global nlp, tokenizer, model
    
    if nlp is None:
        try:
            nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            # Télécharger si non disponible
            spacy.cli.download(settings.SPACY_MODEL)
            nlp = spacy.load(settings.SPACY_MODEL)
    
    if tokenizer is None or model is None:
        tokenizer = CamembertTokenizer.from_pretrained(settings.CAMEMBERT_MODEL)
        model = CamembertModel.from_pretrained(settings.CAMEMBERT_MODEL)

def preprocess_text(text: str) -> Dict[str, Any]:
    """Nettoie et prépare le texte pour l'analyse"""
    # Chargement des modèles si nécessaire
    load_models()
    
    # Normalisation du texte
    text = text.replace('\xa0', ' ')  # Remplace les espaces insécables
    text = re.sub(r'\s+', ' ', text)  # Remplace espaces multiples
    text = re.sub(r'[^\w\s€\/%.,;:+\-()]', ' ', text)  # Garde les caractères utiles
    
    # Découpage en sections (titres et paragraphes)
    sections = {}
    current_section = "header"
    sections[current_section] = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Détection des titres de section (en majuscules, courts, terminés par :)
        if re.match(r'^[A-ZÀ-Ü\s]{3,30}:?\s*$', line):
            current_section = line.strip(':').lower()
            sections[current_section] = []
        else:
            sections[current_section].append(line)
    
    # Traitement par SpaCy pour analyse linguistique
    doc = nlp(text)
    
    return {
        "text": text,
        "sections": sections,
        "doc": doc
    }

class JobPostingExtractor:
    def __init__(self):
        # S'assurer que les modèles sont chargés
        load_models()
        
        self.extractors = {
            "titre": self.extract_title,
            "experience": self.extract_experience,
            "competences": self.extract_skills,
            "formation": self.extract_education,
            "contrat": self.extract_contract_type,
            "localisation": self.extract_location,
            "remuneration": self.extract_salary
        }
        
        # Dictionnaires pour patterns et classification
        self.contract_types = ["CDI", "CDD", "Freelance", "Stage", "Alternance", "Intérim"]
        self.education_patterns = ["Bac+", "Master", "Licence", "Doctorat", "Diplôme", "ingénieur"]
        self.experience_indicators = ["ans d'expérience", "années d'expérience", "ans minimum", "année minimum"]
        
    def parse_job_posting(self, text: str) -> Dict[str, Any]:
        """Parse une fiche de poste complète et retourne les informations extraites avec scores"""
        preprocessed = preprocess_text(text)
        
        results = {}
        confidence = {}
        
        # Extraction de chaque champ
        for field, extractor in self.extractors.items():
            value, score = extractor(preprocessed)
            results[field] = value
            confidence[field] = score
        
        # Calculer un score global
        global_score = self.calculate_confidence_scores(results, preprocessed["doc"])
        confidence.update(global_score)
        
        return {
            "extracted_data": results,
            "confidence_scores": confidence
        }
    
    def extract_title(self, preprocessed: Dict[str, Any]) -> Tuple[str, float]:
        """Extrait le titre du poste"""
        doc = preprocessed["doc"]
        text = preprocessed["text"]
        
        # Stratégie 1: Première section (souvent le titre)
        if "header" in preprocessed["sections"]:
            header = " ".join(preprocessed["sections"]["header"])
            # Limiter aux 10 premiers mots
            title_candidate = " ".join(header.split()[:10])
            
            # Calcul du score basé sur la position et la longueur
            score = min(1.0, (0.8 + (1 / (len(title_candidate.split()) + 1))))
            
            # Bonus si contient des mots-clés de poste
            job_keywords = ["développeur", "ingénieur", "technicien", "responsable", "chef", "directeur"]
            if any(keyword in title_candidate.lower() for keyword in job_keywords):
                score = min(1.0, score + 0.15)
                
            return title_candidate, score
        
        # Stratégie 2: Utiliser spaCy NER pour détecter les titres
        for ent in doc.ents:
            if ent.label_ == "TITLE" or ent.label_ == "PROFESSION":
                return ent.text, 0.85
        
        # Stratégie 3: Utiliser CamemBERT pour une classification
        title_sentences = [sent.text for sent in doc.sents][:3]  # Premières phrases
        
        # Obtenir les embeddings et calculer la similarité avec des titres connus
        # (simplifié pour la démonstration)
        # Dans une implémentation réelle, on utiliserait un classifier fine-tuné
        
        # Stratégie de repli
        first_sentence = list(doc.sents)[0].text if len(list(doc.sents)) > 0 else text[:100]
        return first_sentence, 0.6

    def extract_experience(self, preprocessed: Dict[str, Any]) -> Tuple[str, float]:
        """Extrait l'expérience requise en années"""
        text = preprocessed["text"]
        doc = preprocessed["doc"]
        
        # Stratégie 1: Regex pour les patterns d'années d'expérience
        experience_patterns = [
            r'(\d+[\-\+]?\d*)\s*(?:an(?:s|née(?:s)?)?\s*(?:d[e\'])?expérience)',
            r'expérience\s*(?:de|d\'|\:)?\s*(\d+[\-\+]?\d*)\s*an(?:s|née)?',
            r'minimum\s*(?:de)?\s*(\d+[\-\+]?\d*)\s*an(?:s|née)?'
        ]
        
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                experience = match.group(1)
                # Traitement spécial pour les intervalles (3-5 ans) ou minimum (5+)
                if '-' in experience:
                    min_exp, max_exp = experience.split('-')
                    return f"{min_exp}-{max_exp}", 0.95
                elif '+' in experience:
                    min_exp = experience.replace('+', '')
                    return f"{min_exp}+", 0.95
                else:
                    return experience, 0.95
        
        # Stratégie 2: Recherche contextuelle dans les sections pertinentes
        experience_sections = ["experience", "profil", "prerequis", "qualifications"]
        
        for section_name in experience_sections:
            if section_name in preprocessed["sections"]:
                section_text = " ".join(preprocessed["sections"][section_name])
                
                # Recherche de chiffres suivis de "an" dans cette section
                exp_matches = re.finditer(r'(\d+)[\s\w]{1,10}an', section_text.lower())
                for match in exp_matches:
                    return match.group(1), 0.85
        
        # Stratégie 3: Utiliser CamemBERT pour détecter la phrase parlant d'expérience
        # et analyser son contenu (simplifié pour la démonstration)
        
        # Fallback: pas d'expérience explicite
        return "Non spécifié", 0.3

    def extract_skills(self, preprocessed: Dict[str, Any]) -> Tuple[List[str], float]:
        """Extrait les compétences techniques demandées"""
        doc = preprocessed["doc"]
        text = preprocessed["text"]
        
        # Chercher des sections sur les compétences
        skill_sections = ["competences", "compétences", "technique", "technologies", "stack", "requis"]
        
        skills = []
        top_skills = []
        
        # Stratégie 1: Recherche dans des sections spécifiques
        section_skills = []
        for section_name in skill_sections:
            if section_name in preprocessed["sections"]:
                section_text = " ".join(preprocessed["sections"][section_name])
                
                # Chercher les éléments de liste (•, -, *)
                list_items = re.findall(r'[•\-\*]\s*([\w\s\+\#\./]+)', section_text)
                for item in list_items:
                    section_skills.append(item.strip())
                
                # Traiter le texte avec spaCy pour extraire les entités SKILL
                section_doc = nlp(section_text)
                for ent in section_doc.ents:
                    if ent.label_ == "SKILL" or ent.label_ == "PRODUCT":
                        section_skills.append(ent.text)
                        
        if section_skills:
            top_skills = section_skills
            score = 0.9
        
        # Stratégie 2: Recherche de technologies standards
        tech_stack = ["python", "java", "javascript", "c++", "sql", "react", "angular", "vue", 
                      "node.js", "django", "flask", "spring", "aws", "azure", "docker", "kubernetes",
                      "tensorflow", "pytorch", "nlp", "machine learning", "git", "devops"]
        
        tech_matches = []
        for tech in tech_stack:
            if re.search(r'\b' + re.escape(tech) + r'\b', text.lower()):
                tech_matches.append(tech)
        
        if tech_matches and not top_skills:
            top_skills = tech_matches
            score = 0.75
        elif tech_matches:
            # Ajouter des compétences trouvées mais non présentes dans top_skills
            for tech in tech_matches:
                if not any(tech.lower() in skill.lower() for skill in top_skills):
                    top_skills.append(tech)
            score = 0.9
        
        # Stratégie 3: Utiliser la structure en liste
        bullet_lists = re.findall(r'[•\-\*]\s*([\w\s\+\#\.]+)', text)
        if bullet_lists and not top_skills:
            # Filtrer pour ne garder que ce qui ressemble à des compétences
            filtered_items = [item for item in bullet_lists 
                             if len(item.split()) <= 3 and not item.endswith(':')]
            if filtered_items:
                top_skills = filtered_items[:10]  # Limiter aux 10 premiers
                score = 0.6
        
        if not top_skills:
            return "Non spécifié", 0.3
        
        # Nettoyer et dédupliquer
        clean_skills = []
        for skill in top_skills:
            skill = skill.strip().rstrip('.,;:')
            if skill and len(skill) > 1:
                if skill not in clean_skills:
                    clean_skills.append(skill)
        
        return clean_skills[:15], score  # Limiter à 15 compétences maximum

    def extract_education(self, preprocessed: Dict[str, Any]) -> Tuple[Union[List[str], str], float]:
        """Extrait les exigences de formation/diplômes"""
        text = preprocessed["text"]
        doc = preprocessed["doc"]
        
        # Stratégie 1: Recherche des niveaux d'éducation reconnus
        education_patterns = [
            r'bac\s*\+\s*(\d+)',
            r'(master|licence|doctorat|thèse|ingénieur)',
            r'(diplôme|formation)\s+(\w+)',
            r'(école|université)\s+(\w+)'
        ]
        
        education_matches = []
        for pattern in education_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                if match.group(0):
                    education_matches.append(match.group(0))
        
        # Stratégie 2: Recherche dans les sections dédiées
        education_sections = ["formation", "diplôme", "études", "profil", "qualification"]
        for section_name in education_sections:
            if section_name in preprocessed["sections"]:
                section_text = " ".join(preprocessed["sections"][section_name])
                
                # Chercher les patterns d'éducation
                for pattern in education_patterns:
                    matches = re.finditer(pattern, section_text.lower())
                    for match in matches:
                        if match.group(0) and match.group(0) not in education_matches:
                            education_matches.append(match.group(0))
        
        if education_matches:
            # Nettoyer et dédupliquer
            clean_education = []
            for edu in education_matches:
                edu = edu.strip().rstrip('.,;:')
                if edu and len(edu) > 2:
                    if edu not in clean_education:
                        clean_education.append(edu)
            
            return clean_education, 0.85
        
        # Stratégie 3: Analyse contextuelle avec CamemBERT
        # (simplifiée pour la démonstration)
        
        return "Non spécifié", 0.4

    def extract_contract_type(self, preprocessed: Dict[str, Any]) -> Tuple[str, float]:
        """Extrait le type de contrat"""
        text = preprocessed["text"]
        
        # Stratégie 1: Chercher des types de contrat connus
        contract_types = {
            "CDI": ["cdi", "contrat à durée indéterminée", "permanent"],
            "CDD": ["cdd", "contrat à durée déterminée", "temporaire"],
            "Freelance": ["freelance", "indépendant", "consultant externe"],
            "Stage": ["stage", "internship", "stagiaire"],
            "Alternance": ["alternance", "apprentissage", "contrat pro"],
            "Intérim": ["interim", "intérim", "temporaire"]
        }
        
        for contract_type, patterns in contract_types.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', text.lower()):
                    return contract_type, 0.95
        
        # Stratégie 2: Recherche dans des sections spécifiques
        contract_sections = ["contrat", "type de poste", "informations"]
        
        for section_name in contract_sections:
            if section_name in preprocessed["sections"]:
                section_text = " ".join(preprocessed["sections"][section_name])
                
                for contract_type, patterns in contract_types.items():
                    for pattern in patterns:
                        if re.search(r'\b' + re.escape(pattern) + r'\b', section_text.lower()):
                            return contract_type, 0.9
        
        # Stratégie 3: Recherche par proximité de mots
        doc = preprocessed["doc"]
        for token in doc:
            if token.text.lower() in ["contrat", "poste"]:
                # Examiner la fenêtre de contexte
                context = doc[max(0, token.i - 3):min(len(doc), token.i + 4)]
                context_text = " ".join([t.text.lower() for t in context])
                
                for contract_type, patterns in contract_types.items():
                    for pattern in patterns:
                        if pattern in context_text:
                            return contract_type, 0.8
        
        return "Non spécifié", 0.3

    def extract_location(self, preprocessed: Dict[str, Any]) -> Tuple[str, float]:
        """Extrait la localisation du poste"""
        doc = preprocessed["doc"]
        text = preprocessed["text"]
        
        # Stratégie 1: Utiliser SpaCy NER pour les entités de lieu
        locations = []
        for ent in doc.ents:
            if ent.label_ in ["LOC", "GPE"]:
                locations.append(ent.text)
        
        # Stratégie 2: Rechercher des patterns explicites
        location_patterns = [
            r'(?:situé|basé|localisé|lieu)\s*(?:à|en|au)?\s*:?\s*([\w\s-]+)',
            r'(?:poste|emploi)\s*(?:à|en|au)?\s*:?\s*([\w\s-]+)',
            r'(?:siège|bureaux)\s*(?:à|en|au)?\s*:?\s*([\w\s-]+)'
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                location = match.group(1).strip()
                # Vérifier si c'est une vraie localisation et pas un mot commun
                if len(location) > 2 and not any(location.lower() == common for common in ["france", "l'entreprise"]):
                    locations.append(location)
        
        # Stratégie 3: Chercher dans des sections spécifiques
        location_sections = ["lieu", "localisation", "informations", "entreprise"]
        
        for section_name in location_sections:
            if section_name in preprocessed["sections"]:
                section_text = " ".join(preprocessed["sections"][section_name])
                
                # Réutiliser spaCy NER
                section_doc = nlp(section_text)
                for ent in section_doc.ents:
                    if ent.label_ in ["LOC", "GPE"]:
                        locations.append(ent.text)
        
        if locations:
            # Nettoyer et dédupliquer
            clean_locations = []
            for loc in locations:
                loc = loc.strip().rstrip('.,;:')
                if loc and len(loc) > 2:
                    if not any(loc.lower() == l.lower() for l in clean_locations):
                        clean_locations.append(loc)
            
            # Prendre la localisation la plus mentionnée
            if clean_locations:
                from collections import Counter
                location_counter = Counter(clean_locations)
                top_location = location_counter.most_common(1)[0][0]
                return top_location, 0.9
        
        return "Non spécifié", 0.4

    def extract_salary(self, preprocessed: Dict[str, Any]) -> Tuple[str, float]:
        """Extrait les informations de rémunération"""
        text = preprocessed["text"]
        
        # Stratégie 1: Regex pour les patterns de salaire standards
        salary_patterns = [
            # Format avec K€
            r'(\d+[.,]?\d*)\s*[kK][€e]',
            r'(\d+[.,]?\d*)\s*[à-]\s*(\d+[.,]?\d*)\s*[kK][€e]',
            
            # Format avec euros
            r'(\d+[.,]?\d*)\s*(?:€|[eE]uro)',
            r'(\d+[.,]?\d*)\s*[à-]\s*(\d+[.,]?\d*)\s*(?:€|[eE]uro)',
            
            # Format avec € ou euro/mois/an
            r'(\d+[.,]?\d*)\s*(?:k)?(?:€|[eE]uro)(?:\s*\/\s*(?:mois|an|année|annuel))?',
            r'(\d+[.,]?\d*)\s*[à-]\s*(\d+[.,]?\d*)\s*(?:k)?(?:€|[eE]uro)(?:\s*\/\s*(?:mois|an|année|annuel))?',
            
            # Format général
            r'salaire\s*(?:de|:)?\s*(\d+[.,]?\d*)',
            r'rémunération\s*(?:de|:)?\s*(\d+[.,]?\d*)',
            r'package\s*(?:de|:)?\s*(\d+[.,]?\d*)'
        ]
        
        for pattern in salary_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if match.group(1):
                    # Fourchette de salaire
                    if len(match.groups()) > 1 and match.group(2):
                        min_val = match.group(1)
                        max_val = match.group(2)
                        
                        # Vérifier si c'est en K€
                        if 'k' in match.group(0).lower() or 'K' in match.group(0):
                            return f"{min_val}K€-{max_val}K€", 0.95
                        else:
                            return f"{min_val}€-{max_val}€", 0.95
                    else:
                        # Salaire unique
                        val = match.group(1)
                        if 'k' in match.group(0).lower() or 'K' in match.group(0):
                            return f"{val}K€", 0.95
                        else:
                            return f"{val}€", 0.95
        
        # Stratégie 2: Recherche dans des sections spécifiques
        salary_sections = ["salaire", "rémunération", "package", "avantages"]
        
        for section_name in salary_sections:
            if section_name in preprocessed["sections"]:
                section_text = " ".join(preprocessed["sections"][section_name])
                
                # Réutiliser les patterns
                for pattern in salary_patterns:
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        if match.group(1):
                            if len(match.groups()) > 1 and match.group(2):
                                min_val = match.group(1)
                                max_val = match.group(2)
                                
                                if 'k' in match.group(0).lower() or 'K' in match.group(0):
                                    return f"{min_val}K€-{max_val}K€", 0.9
                                else:
                                    return f"{min_val}€-{max_val}€", 0.9
                            else:
                                val = match.group(1)
                                if 'k' in match.group(0).lower() or 'K' in match.group(0):
                                    return f"{val}K€", 0.9
                                else:
                                    return f"{val}€", 0.9
        
        # Stratégie 3: Analyse contextuelle pour des termes comme "competitive", "selon profil"
        contextual_salary_terms = ["selon profil", "selon expérience", "compétitif", "attractif", "négociable"]
        
        for term in contextual_salary_terms:
            if term in text.lower():
                return term.capitalize(), 0.7
        
        return "Non spécifié", 0.3
        
    def calculate_confidence_scores(self, extracted_data: Dict[str, Any], doc) -> Dict[str, float]:
        """Calcule des scores de confiance raffinés pour les données extraites"""
        
        scores = {}
        
        # 1. Score basé sur la complétude des données
        completeness = sum(1 for value in extracted_data.values() 
                          if value and value != "Non spécifié") / len(extracted_data)
        
        # 2. Score basé sur la qualité des correspondances de patterns
        # Déjà calculé dans chaque extracteur
        
        # 3. Score basé sur la cohérence entre les champs
        coherence_score = 1.0
        
        # Exemple: cohérence entre titre et compétences
        if extracted_data.get("titre") and extracted_data.get("competences"):
            titre = extracted_data["titre"].lower()
            competences = [c.lower() for c in extracted_data["competences"]] if isinstance(extracted_data["competences"], list) else []
            
            # Vérifier si des compétences sont mentionnées dans le titre
            title_skills_overlap = any(skill in titre for skill in competences)
            if not title_skills_overlap:
                coherence_score *= 0.9
        
        # 4. Bonus pour extraction dans des sections nommées explicitement
        # (intégré dans les extracteurs individuels)
        
        # Score final global: moyenne pondérée des différents scores
        global_score = 0.5 * completeness + 0.5 * coherence_score
        scores["global"] = round(global_score, 2)
        
        return scores

# Fonction d'interface simple
def parse_job_description(text: str) -> Dict[str, Any]:
    """Point d'entrée principal pour le parsing d'une fiche de poste"""
    extractor = JobPostingExtractor()
    return extractor.parse_job_posting(text)