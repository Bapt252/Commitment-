import re
import spacy
from typing import Dict, List, Any, Optional
import logging

class SectionExtractor:
    """
    Extracteur de sections pour documents CV et offres d'emploi
    """
    def __init__(self, nlp=None):
        """
        Initialise l'extracteur avec un modèle spaCy optionnel
        
        Args:
            nlp: Modèle spaCy préchargé (optionnel)
        """
        # Initialiser spaCy si nécessaire
        if nlp is None:
            try:
                self.nlp = spacy.load("fr_core_news_lg")
            except OSError:
                try:
                    spacy.cli.download("fr_core_news_lg")
                    self.nlp = spacy.load("fr_core_news_lg")
                except:
                    self.nlp = None
                    logging.warning("Impossible de charger spaCy, certaines fonctionnalités seront limitées")
        else:
            self.nlp = nlp
        
        # Modèles de titres de section par type de document
        self.cv_section_patterns = {
            'experience': [
                r'exp[ée]riences?\\s+professionnelles?',
                r'parcours\\s+professionnel',
                r'carri[èe]re\\s+professionnelle',
                r'emplois?\\s+pr[ée]c[ée]dents?'
            ],
            'education': [
                r'[ée]ducation', r'formations?', r'cursus',
                r'parcours\\s+acad[ée]mique', r'dipl[ôo]mes?',
                r'[ée]tudes', r'scolarit[ée]'
            ],
            'skills': [
                r'comp[ée]tences?', r'aptitudes?', r'savoir[\\s-]faire',
                r'qualifications?', r'connaissances?', r'expertise',
                r'outils', r'technologies'
            ],
            'languages': [
                r'langues?', r'comp[ée]tences?\\s+linguistiques?',
                r'niveau\\s+de\\s+langue'
            ],
            'interests': [
                r'centres?\\s+d\\\'int[ée]r[êe]ts?', r'loisirs?',
                r'activit[ée]s\\s+extra[\\s-]professionnelles?',
                r'hobbies?', r'passions?'
            ],
            'profile': [
                r'profil', r'[àa]\\s+propos(\\s+de\\s+moi)?', r'r[ée]sum[ée]',
                r'pr[ée]sentation', r'objectifs?(\\s+professionnels?)?',
                r'projet\\s+professionnel'
            ],
            'contact': [
                r'coordonn[ée]es?', r'contact', 
                r'informations?\\s+personnelles?'
            ]
        }
        
        self.job_section_patterns = {
            'company': [
                r'entreprise', r'soci[ée]t[ée]', r'qui\\s+sommes[\\s-]nous',
                r'[àa]\\s+propos(\\s+de\\s+nous)?', r'notre\\s+entreprise',
                r'pr[ée]sentation'
            ],
            'responsibilities': [
                r'missions?', r'responsabilit[ée]s?', r'attributions?', 
                r't[âa]ches?', r'activit[ée]s?', r'objectifs?',
                r'r[ôo]les?', r'travail\\s+[àa]\\s+r[ée]aliser'
            ],
            'requirements': [
                r'profil\\s+recherch[ée]', r'qualifications?(\\s+requises?)?',
                r'comp[ée]tences?(\\s+requises?)?', r'pr[ée]-requis',
                r'exigences?', r'aptitudes?', r'exp[ée]rience\\s+requise'
            ],
            'benefits': [
                r'avantages?', r'b[ée]n[ée]fices?', r'r[ée]mun[ée]ration',
                r'salaire', r'package', r'nous\\s+offrons', r'pourquoi\\s+nous\\s+rejoindre'
            ],
            'contract': [
                r'type\\s+de\\s+contrat', r'contrat', r'conditions?',
                r'modalit[ée]s', r'dur[ée]e', r'temps\\s+de\\s+travail'
            ]
        }
        
    def extract_sections(self, text: str, doc_type: str) -> Dict[str, List[str]]:
        """
        Extraction améliorée des sections avec analyse structurelle et sémantique
        
        Args:
            text: Texte du document
            doc_type: Type de document ('cv' ou 'job_posting')
            
        Returns:
            Dict: Sections extraites avec leur contenu
        """
        sections = {'header': []}
        section_patterns = (self.cv_section_patterns if doc_type == 'cv' 
                           else self.job_section_patterns)
        
        # Préparation du texte
        lines = text.split('\n')
        
        # Première passe: détection des titres de section par formatage
        format_sections = self._detect_sections_by_format(lines)
        
        # Deuxième passe: détection par contenu sémantique
        content_sections = self._detect_sections_by_content(lines, section_patterns)
        
        # Fusion des résultats des deux approches
        section_positions = self._merge_section_results(format_sections, content_sections)
        
        # Affectation du contenu aux sections
        return self._assign_content_to_sections(lines, section_positions)
    
    def _detect_sections_by_format(self, lines: List[str]) -> Dict[str, int]:
        """
        Détecte les sections en se basant sur le formatage (majuscules, etc.)
        
        Args:
            lines: Lignes du document
            
        Returns:
            Dict: Titres de section avec positions (numéros de ligne)
        """
        format_sections = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Détection par mise en forme
            if (re.match(r'^[A-Z\s]{3,30}[\s:]*$', line) or 
                (line.endswith(':') and len(line) < 40) or
                (len(line.split()) <= 3 and i > 0 and not lines[i-1].strip() 
                 and i < len(lines)-1 and not lines[i+1].strip())):
                
                # C'est probablement un titre de section
                section_name = line.strip(':').lower()
                format_sections[section_name] = i
        
        return format_sections
    
    def _detect_sections_by_content(self, lines: List[str], 
                                   section_patterns: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Détecte les sections en utilisant le contenu sémantique
        
        Args:
            lines: Lignes du document
            section_patterns: Patterns de reconnaissance par type de section
            
        Returns:
            Dict: Types de section avec positions (numéros de ligne)
        """
        content_sections = {}
        
        # Recombiner les lignes pour les recherches regex
        text = '\n'.join(lines)
        
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Trouver le numéro de ligne correspondant à cette position
                    pos = match.start()
                    line_num = text[:pos].count('\n')
                    
                    # Ne prendre que la première occurrence pour chaque type
                    if section_type not in content_sections:
                        content_sections[section_type] = line_num
        
        return content_sections
    
    def _merge_section_results(self, format_sections: Dict[str, int], 
                              content_sections: Dict[str, int]) -> Dict[str, int]:
        """
        Fusionne les résultats des différentes méthodes de détection
        
        Args:
            format_sections: Sections détectées par formatage
            content_sections: Sections détectées par contenu
            
        Returns:
            Dict: Sections fusionnées avec positions
        """
        merged = {}
        
        # Ajouter les sections détectées par format
        for section, line_num in format_sections.items():
            merged[section] = line_num
        
        # Ajouter/mettre à jour avec les sections détectées par contenu
        for section_type, line_num in content_sections.items():
            # Si une section similaire existe déjà, on garde celle avec le meilleur nom
            similar_exists = False
            
            for existing_section, existing_line in list(merged.items()):
                # Si on a détecté la même ligne, prendre le nom le plus significatif
                if abs(existing_line - line_num) <= 2:
                    similar_exists = True
                    if len(existing_section) > 20 and len(section_type) < 20:
                        merged[section_type] = merged.pop(existing_section)
                    break
            
            if not similar_exists:
                merged[section_type] = line_num
        
        return merged
    
    def _assign_content_to_sections(self, lines: List[str], 
                                   section_starts: Dict[str, int]) -> Dict[str, List[str]]:
        """
        Affecte le contenu aux sections détectées
        
        Args:
            lines: Lignes du document
            section_starts: Positions de début des sections
            
        Returns:
            Dict: Sections avec leur contenu
        """
        sections_with_content = {'header': []}
        
        # Si aucune section n'a été détectée, tout va dans l'en-tête
        if not section_starts:
            sections_with_content['header'] = [line.strip() for line in lines if line.strip()]
            return sections_with_content
        
        # Trier les sections par position dans le document
        ordered_sections = sorted(section_starts.items(), key=lambda x: x[1])
        
        # Assigner le contenu de l'en-tête
        header_end = ordered_sections[0][1]
        sections_with_content['header'] = [line.strip() for line in lines[:header_end] if line.strip()]
        
        # Assigner le contenu des autres sections
        for i, (section_name, start_line) in enumerate(ordered_sections):
            end_line = (ordered_sections[i+1][1] if i < len(ordered_sections) - 1 
                       else len(lines))
            
            # Exclure la ligne du titre elle-même
            section_content = [line.strip() for line in lines[start_line+1:end_line] if line.strip()]
            sections_with_content[section_name] = section_content
        
        return sections_with_content
