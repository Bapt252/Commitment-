import re
import spacy
import json
from typing import Dict, List, Tuple, Any, Optional, Union
from pathlib import Path
import logging

class CompanyQuestionnaireExtractor:
    """
    Classe pour analyser les questionnaires d'entreprise et extraire les informations pertinentes
    qui seront utilisées pour le matching avec les candidats.
    """
    
    def __init__(self):
        # Chargement du modèle SpaCy
        try:
            self.nlp = spacy.load("fr_core_news_lg")
        except OSError:
            spacy.cli.download("fr_core_news_lg")
            self.nlp = spacy.load("fr_core_news_lg")
        
        self.logger = logging.getLogger(__name__)
        
        # Dictionnaires pour les patterns de valeurs et culture d'entreprise
        self.values_keywords = {
            "innovation": ["innovation", "créativité", "disruptif", "avant-garde", "pionnier", "nouvelle technologie"],
            "collaboration": ["collaboration", "équipe", "entraide", "cohésion", "ensemble", "collectif"],
            "excellence": ["excellence", "qualité", "performance", "rigueur", "exigence", "précision"],
            "respect": ["respect", "tolérance", "inclusion", "diversité", "écoute", "bienveillance"],
            "autonomie": ["autonomie", "indépendance", "responsabilisation", "liberté", "initiative"],
            "equilibre": ["équilibre", "bien-être", "work-life balance", "flexibilité", "télétravail"]
        }
        
        self.company_size_patterns = {
            "startup": ["startup", "jeune pousse", "early stage", "seed", "amorçage"],
            "pme": ["pme", "petite entreprise", "moyenne entreprise", "tpe", "entreprise familiale"],
            "grande_entreprise": ["grande entreprise", "groupe", "multinational", "corporate"],
            "scale_up": ["scale-up", "hypercroissance", "croissance rapide", "licorne"]
        }
        
        self.work_environment_patterns = {
            "remote": ["remote", "télétravail", "travail à distance", "full remote", "home office"],
            "hybrid": ["hybride", "mixte", "flexible", "combinaison bureau télétravail"],
            "office": ["présentiel", "bureau", "open space", "locaux", "site"],
            "international": ["international", "étranger", "global", "monde", "pays"]
        }
        
        # Chargement de taxonomies supplémentaires (à implémenter avec fichiers JSON)
        self.load_taxonomies()
    
    def load_taxonomies(self):
        """
        Charge les taxonomies externes depuis les fichiers JSON
        """
        try:
            taxonomies_path = Path(__file__).resolve().parent.parent.parent / "data"
            
            # Charger les taxonomies si les fichiers existent
            company_values_path = taxonomies_path / "company_values_taxonomy.json"
            if company_values_path.exists():
                with open(company_values_path, 'r', encoding='utf-8') as f:
                    self.values_keywords.update(json.load(f))
                    
            sectors_path = taxonomies_path / "industry_sectors.json"
            if sectors_path.exists():
                with open(sectors_path, 'r', encoding='utf-8') as f:
                    self.industry_sectors = json.load(f)
            else:
                # Fallback sur des secteurs par défaut
                self.industry_sectors = {
                    "tech": ["technologie", "informatique", "digital", "numérique", "IT", "logiciel"],
                    "finance": ["finance", "banque", "assurance", "investissement", "fintech"],
                    "sante": ["santé", "médical", "pharmaceutique", "biotech", "hôpital"],
                    "education": ["éducation", "formation", "enseignement", "edtech", "école"],
                    "industrie": ["industrie", "manufacture", "production", "usine", "fabrication"],
                    "services": ["services", "conseil", "consulting", "RH", "marketing"]
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des taxonomies: {e}")
            # Utiliser les valeurs par défaut définies dans __init__
    
    def parse_company_questionnaire(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse un questionnaire d'entreprise complet
        
        Args:
            data: Dictionnaire contenant les réponses au questionnaire
            
        Returns:
            Dict: Informations structurées extraites
        """
        try:
            results = {}
            confidence = {}
            
            # 1. Informations de base de l'entreprise
            if "company_info" in data:
                results["company_info"] = data["company_info"]
            
            # 2. Extraction des valeurs et culture
            values_data, values_confidence = self.extract_company_values(data)
            results["values"] = values_data
            confidence["values"] = values_confidence
            
            # 3. Extraction de l'environnement de travail
            environment_data, environment_confidence = self.extract_work_environment(data)
            results["work_environment"] = environment_data
            confidence["work_environment"] = environment_confidence
            
            # 4. Extraction du secteur d'activité
            if "sector" in data:
                sector_data, sector_confidence = self.analyze_industry_sector(data["sector"])
                results["industry_sector"] = sector_data
                confidence["industry_sector"] = sector_confidence
            
            # 5. Taille et maturité de l'entreprise
            if "company_size" in data or "employee_count" in data:
                size_data, size_confidence = self.analyze_company_size(data)
                results["company_size"] = size_data
                confidence["company_size"] = size_confidence
            
            # 6. Analyse des technologies et compétences recherchées
            tech_data, tech_confidence = self.extract_tech_stack(data)
            results["technologies"] = tech_data
            confidence["technologies"] = tech_confidence
            
            # Calcul du score global
            global_score = sum(confidence.values()) / len(confidence)
            confidence["global"] = round(global_score, 2)
            
            return {
                "extracted_data": results,
                "confidence_scores": confidence
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse du questionnaire: {e}")
            # Retourner un résultat minimal en cas d'erreur
            return {
                "extracted_data": {"error": "Erreur d'analyse du questionnaire"},
                "confidence_scores": {"global": 0.3}
            }
    
    def extract_company_values(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Extrait et analyse les valeurs et la culture d'entreprise
        
        Args:
            data: Données du questionnaire
            
        Returns:
            Tuple: (valeurs extraites, score de confiance)
        """
        values_result = {}
        score = 0.5  # Score de confiance de base
        
        # Récupérer le texte pertinent des différentes parties du questionnaire
        values_text = ""
        relevant_fields = ["company_values", "culture", "mission", "vision", "about", "description"]
        
        for field in relevant_fields:
            if field in data and data[field]:
                values_text += data[field] + " "
        
        # Si un champ explicite des valeurs existe, on l'utilise directement
        if "values" in data and isinstance(data["values"], list):
            explicit_values = data["values"]
            values_result["explicit_values"] = explicit_values
            score = 0.9
        else:
            # Extraire les valeurs du texte
            extracted_values = {}
            
            # Analyse du texte avec NLP
            doc = self.nlp(values_text.lower())
            
            # Compter les occurrences de mots-clés par catégorie
            for category, keywords in self.values_keywords.items():
                score_category = 0
                for keyword in keywords:
                    # Recherche de mots-clés et de proximité sémantique
                    if any(keyword in sent.text.lower() for sent in doc.sents):
                        score_category += 1
                
                # Normaliser par le nombre de mots-clés
                if keywords:
                    normalized_score = min(1.0, score_category / len(keywords))
                    if normalized_score > 0.1:  # Seuil minimal pour éviter le bruit
                        extracted_values[category] = round(normalized_score, 2)
            
            # Tri par importance
            sorted_values = sorted(extracted_values.items(), key=lambda x: x[1], reverse=True)
            values_result["detected_values"] = dict(sorted_values[:5])  # Top 5 des valeurs
            
            # Ajustement du score de confiance
            if sorted_values:
                score = min(0.85, 0.5 + (len(sorted_values) * 0.05))
        
        return values_result, score
    
    def extract_work_environment(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Analyse l'environnement de travail préféré de l'entreprise
        
        Args:
            data: Données du questionnaire
            
        Returns:
            Tuple: (informations sur l'environnement, score de confiance)
        """
        environment_result = {}
        score = 0.5  # Score de confiance de base
        
        # Champs potentiels contenant des informations sur l'environnement
        environment_fields = ["work_environment", "benefits", "perks", "workplace"]
        environment_text = ""
        
        for field in environment_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    environment_text += data[field] + " "
                elif isinstance(data[field], list):
                    environment_text += " ".join(data[field]) + " "
        
        # Si des champs explicites existent, on les utilise
        if "remote_policy" in data:
            environment_result["remote_policy"] = data["remote_policy"]
            score += 0.2
        
        if "office_locations" in data:
            environment_result["locations"] = data["office_locations"]
            score += 0.1
        
        # Analyser le texte pour détecter des patterns d'environnement de travail
        for env_type, patterns in self.work_environment_patterns.items():
            for pattern in patterns:
                if re.search(r'\\b' + re.escape(pattern) + r'\\b', environment_text.lower()):
                    if "work_mode" not in environment_result:
                        environment_result["work_mode"] = []
                    
                    if env_type not in environment_result["work_mode"]:
                        environment_result["work_mode"].append(env_type)
                        score += 0.05
        
        # Si on a détecté un mode de travail, on augmente le score
        if "work_mode" in environment_result:
            score = min(0.9, score)
        
        # S'il y a des avantages sociaux mentionnés explicitement
        if "benefits" in data and isinstance(data["benefits"], list):
            environment_result["benefits"] = data["benefits"]
            score += 0.1
        
        return environment_result, min(0.95, score)
    
    def analyze_industry_sector(self, sector_text: str) -> Tuple[Dict[str, Any], float]:
        """
        Analyse et classifie le secteur d'activité de l'entreprise
        
        Args:
            sector_text: Texte décrivant le secteur d'activité
            
        Returns:
            Tuple: (secteur identifié avec confiance, score global)
        """
        sector_result = {}
        confidence = 0.5
        
        # Nettoyage du texte
        sector_text = sector_text.lower().strip()
        
        # Correspondance exacte d'abord (si le texte correspond exactement à un secteur)
        exact_match = False
        for sector, keywords in self.industry_sectors.items():
            if sector_text in keywords:
                sector_result["primary_sector"] = sector
                confidence = 0.9
                exact_match = True
                break
        
        if not exact_match:
            # Recherche de mots-clés dans le texte
            sector_scores = {}
            for sector, keywords in self.industry_sectors.items():
                score = 0
                for keyword in keywords:
                    if keyword in sector_text:
                        score += 1
                
                if score > 0:
                    sector_scores[sector] = score
            
            # Trier par score et extraire les plus pertinents
            if sector_scores:
                sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
                
                # Secteur principal
                primary_sector = sorted_sectors[0][0]
                sector_result["primary_sector"] = primary_sector
                confidence = min(0.85, 0.5 + (sorted_sectors[0][1] * 0.1))
                
                # Secteurs secondaires (s'il y en a)
                if len(sorted_sectors) > 1:
                    secondary_sectors = [s[0] for s in sorted_sectors[1:3]]  # Jusqu'à 2 secteurs secondaires
                    sector_result["secondary_sectors"] = secondary_sectors
        
        # Si aucun secteur détecté, utiliser "other"
        if not sector_result:
            sector_result["primary_sector"] = "other"
            confidence = 0.3
        
        return sector_result, confidence
    
    def analyze_company_size(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Analyse la taille et la maturité de l'entreprise
        
        Args:
            data: Données du questionnaire
            
        Returns:
            Tuple: (informations de taille, score de confiance)
        """
        size_result = {}
        confidence = 0.5
        
        # Récupération directe si disponible
        if "employee_count" in data:
            try:
                # Tentative de conversion en nombre
                count = int(data["employee_count"])
                size_result["employee_count"] = count
                
                # Classification par taille
                if count < 10:
                    size_result["size_category"] = "micro"
                elif count < 50:
                    size_result["size_category"] = "small"
                elif count < 250:
                    size_result["size_category"] = "medium"
                else:
                    size_result["size_category"] = "large"
                
                confidence = 0.9
                
            except (ValueError, TypeError):
                # Si ce n'est pas un nombre, on essaie de détecter des patterns
                size_text = str(data["employee_count"]).lower()
                
                if "moins de 10" in size_text or "<10" in size_text:
                    size_result["size_category"] = "micro"
                    confidence = 0.8
                elif any(x in size_text for x in ["10-50", "moins de 50", "<50"]):
                    size_result["size_category"] = "small"
                    confidence = 0.8
                elif any(x in size_text for x in ["50-250", "moins de 250", "<250"]):
                    size_result["size_category"] = "medium"
                    confidence = 0.8
                elif any(x in size_text for x in [">250", "plus de 250", "grande"]):
                    size_result["size_category"] = "large"
                    confidence = 0.8
        
        # Détection du type d'entreprise
        company_type = None
        highest_score = 0
        
        # Chercher dans les descriptions ou le type d'entreprise
        company_text = ""
        if "company_type" in data:
            company_text += data["company_type"] + " "
        if "description" in data:
            company_text += data["description"] + " "
        if "about" in data:
            company_text += data["about"] + " "
        
        for type_name, patterns in self.company_size_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in company_text.lower():
                    score += 1
            
            if score > highest_score:
                highest_score = score
                company_type = type_name
        
        if company_type:
            size_result["company_type"] = company_type
            confidence = max(confidence, min(0.85, 0.5 + (highest_score * 0.1)))
        
        if not size_result:
            size_result["size_category"] = "unknown"
            confidence = 0.3
        
        return size_result, confidence
    
    def extract_tech_stack(self, data: Dict[str, Any]) -> Tuple[List[str], float]:
        """
        Extrait la stack technologique et les compétences recherchées
        
        Args:
            data: Données du questionnaire
            
        Returns:
            Tuple: (liste de technologies, score de confiance)
        """
        tech_stack = []
        confidence = 0.5
        
        # Liste de technologies courantes à détecter
        common_techs = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js", 
            "php", "ruby", "c++", "c#", ".net", "django", "flask", "spring", 
            "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", 
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", 
            "git", "jira", "confluence", "agile", "scrum", "devops", "ci/cd",
            "tensorflow", "pytorch", "machine learning", "data science", "ai"
        ]
        
        # Champs potentiels contenant des technologies
        tech_fields = ["technologies", "tech_stack", "skills_required", "technical_environment"]
        
        # Extraction directe si disponible
        for field in tech_fields:
            if field in data:
                if isinstance(data[field], list):
                    tech_stack.extend(data[field])
                    confidence = 0.9
                elif isinstance(data[field], str):
                    # Essayer de détecter les technologies dans le texte
                    tech_text = data[field].lower()
                    for tech in common_techs:
                        if re.search(r'\\b' + re.escape(tech) + r'\\b', tech_text):
                            tech_stack.append(tech)
                    
                    if tech_stack:
                        confidence = 0.8
        
        # Si pas de technologies détectées, chercher dans d'autres champs
        if not tech_stack:
            if "job_description" in data:
                tech_text = data["job_description"].lower()
                for tech in common_techs:
                    if re.search(r'\\b' + re.escape(tech) + r'\\b', tech_text):
                        tech_stack.append(tech)
                
                if tech_stack:
                    confidence = 0.7
        
        # Dédupliquer et nettoyer
        tech_stack = list(set(tech_stack))
        
        if not tech_stack:
            return ["Non spécifié"], 0.3
        
        return tech_stack, confidence

# Fonction d'interface
def parse_company_questionnaire(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Point d'entrée principal pour l'analyse des questionnaires d'entreprise
    
    Args:
        data: Données du questionnaire à analyser
        
    Returns:
        Dict: Informations extraites avec scores de confiance
    """
    extractor = CompanyQuestionnaireExtractor()
    return extractor.parse_company_questionnaire(data)
