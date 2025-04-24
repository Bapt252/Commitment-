
"""
Nexten Matcher - Algorithme de matching intelligent
---------------------------------------------------
Ce module implémente un algorithme avancé de matching entre les profils candidats et les offres d'emploi.
Il intègre les trois phases du processus Nexten:
1. Parsing CV via OpenAI
2. Questionnaires candidat et entreprise
3. Matching intelligent combinant ces sources de données

Auteur: Claude/Anthropic
Date: 24/04/2025
"""

import re
import math
import logging
from typing import Dict, List, Any, Tuple, Optional, Union

# Configuration du logger
logger = logging.getLogger(__name__)

class NextenMatchingAlgorithm:
    """
    Algorithme de matching intelligent pour Nexten intégrant CV et questionnaires
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialiser l'algorithme avec une configuration personnalisable
        
        Args:
            config: Configuration personnalisée (poids, seuils, etc.)
        """
        # Configuration par défaut
        self.config = {
            'weights': {
                # Poids du CV
                'cv_skills': 0.25,
                'cv_experience': 0.15,
                'cv_description': 0.10,
                'cv_title': 0.05,
                
                # Poids des sections du questionnaire
                'informations_personnelles': 0.05,
                'mobilite_preferences': 0.15,
                'motivations_secteurs': 0.15,
                'disponibilite_situation': 0.10,
            },
            'thresholds': {
                'minimum_score': 0.3,  # Score minimum pour considérer un match
                'excellent_match': 0.85  # Seuil pour un très bon match
            },
            'skills_config': {
                'essential_bonus': 1.5,  # Bonus pour compétences essentielles
                'nice_to_have_factor': 0.7  # Facteur pour compétences souhaitées
            },
            'questionnaire_config': {
                'preference_match_boost': 0.1,  # Bonus quand préférences correspondent
                'culture_mismatch_penalty': 0.15,  # Pénalité si mauvais match culturel
                'essential_skills_weight': 1.5,  # Poids pour compétences essentielles
            }
        }
        
        # Surcharge avec la configuration personnalisée
        if config:
            self._update_config(config)
    
    def _update_config(self, custom_config: Dict[str, Any]) -> None:
        """
        Mettre à jour la configuration avec des valeurs personnalisées
        
        Args:
            custom_config: Dictionnaire de configuration personnalisée
        """
        for category, values in custom_config.items():
            if category in self.config:
                if isinstance(self.config[category], dict):
                    self.config[category].update(values)
                else:
                    self.config[category] = values
    
    def calculate_match(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculer le score de correspondance en intégrant CV et questionnaires
        
        Args:
            candidate_data: Données complètes du candidat (CV + questionnaire)
            job_data: Données complètes du job (description + questionnaire)
            
        Returns:
            dict: Résultat du matching avec score global et détails
        """
        # 1. Extraction des données
        cv_data = candidate_data.get('cv', {})
        candidate_questionnaire = candidate_data.get('questionnaire', {})
        job_description = job_data.get('description', {})
        company_questionnaire = job_data.get('questionnaire', {})
        
        # 2. Scores basés sur le CV
        cv_skills_score = self._calculate_skills_match(
            cv_data.get('skills', []),
            job_description.get('required_skills', []),
            job_description.get('preferred_skills', [])
        )
        
        cv_experience_score = self._calculate_experience_match(
            cv_data.get('experience', ''),
            job_description.get('required_experience', '')
        )
        
        cv_description_score = self._calculate_description_match(
            cv_data.get('summary', ''),
            job_description.get('description', '')
        )
        
        cv_title_score = self._calculate_title_match(
            cv_data.get('job_title', ''),
            job_description.get('title', '')
        )
        
        # 3. Scores basés sur les questionnaires
        questionnaire_scores = self._calculate_questionnaire_match(
            candidate_questionnaire,
            company_questionnaire
        )
        
        # 4. Combinaison des scores avec pondération
        weights = self.config['weights']
        
        # Scores du CV
        cv_score = (
            cv_skills_score * weights['cv_skills'] +
            cv_experience_score * weights['cv_experience'] +
            cv_description_score * weights['cv_description'] +
            cv_title_score * weights['cv_title']
        ) / (weights['cv_skills'] + weights['cv_experience'] + weights['cv_description'] + weights['cv_title'])
        
        # Calcul du score final, combinant CV et questionnaires
        total_cv_weight = weights['cv_skills'] + weights['cv_experience'] + weights['cv_description'] + weights['cv_title']
        total_questionnaire_weight = weights['informations_personnelles'] + weights['mobilite_preferences'] + weights['motivations_secteurs'] + weights['disponibilite_situation']
        
        # Score global normalisé
        total_score = (
            cv_score * total_cv_weight +
            questionnaire_scores['total'] * total_questionnaire_weight
        ) / (total_cv_weight + total_questionnaire_weight)
        
        # Classification du match
        match_category = self._classify_match(total_score)
        
        return {
            'score': round(total_score, 2),
            'category': match_category,
            'details': {
                'cv': {
                    'total': round(cv_score, 2),
                    'skills': round(cv_skills_score, 2),
                    'experience': round(cv_experience_score, 2),
                    'description': round(cv_description_score, 2),
                    'title': round(cv_title_score, 2)
                },
                'questionnaire': {
                    'total': round(questionnaire_scores['total'], 2),
                    'informations_personnelles': round(questionnaire_scores['informations_personnelles'], 2),
                    'mobilite_preferences': round(questionnaire_scores['mobilite_preferences'], 2),
                    'motivations_secteurs': round(questionnaire_scores['motivations_secteurs'], 2),
                    'disponibilite_situation': round(questionnaire_scores['disponibilite_situation'], 2)
                }
            },
            'insights': self._generate_match_insights(
                candidate_data, 
                job_data, 
                total_score,
                questionnaire_scores
            )
        }
    
    def _calculate_skills_match(self, candidate_skills: List[str], 
                               required_skills: List[str], 
                               preferred_skills: Optional[List[str]] = None) -> float:
        """
        Calculer la correspondance des compétences avec distinction entre 
        compétences requises et préférées
        
        Args:
            candidate_skills: Liste des compétences du candidat
            required_skills: Liste des compétences requises
            preferred_skills: Liste des compétences préférées (optionnel)
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        if not candidate_skills or not required_skills:
            return 0.0
        
        # Normalisation des compétences
        normalized_candidate_skills = [self._normalize_text(skill) for skill in candidate_skills]
        normalized_required_skills = [self._normalize_text(skill) for skill in required_skills]
        
        # Compétences préférées (si fournies)
        normalized_preferred_skills = []
        if preferred_skills:
            normalized_preferred_skills = [self._normalize_text(skill) for skill in preferred_skills]
        
        # Correspondance avec compétences requises
        matched_required = self._get_matched_skills(normalized_candidate_skills, normalized_required_skills)
        required_score = len(matched_required) / len(normalized_required_skills) if normalized_required_skills else 0
        
        # Correspondance avec compétences préférées
        preferred_score = 0
        if normalized_preferred_skills:
            matched_preferred = self._get_matched_skills(normalized_candidate_skills, normalized_preferred_skills)
            preferred_score = len(matched_preferred) / len(normalized_preferred_skills) * self.config['skills_config']['nice_to_have_factor']
        
        # Score combiné (avec plus de poids pour les compétences requises)
        if preferred_score > 0:
            # Formule qui priorise les compétences requises mais valorise aussi les préférées
            total_skills = len(normalized_required_skills) + (len(normalized_preferred_skills) * self.config['skills_config']['nice_to_have_factor'])
            score = (len(matched_required) + (len(matched_preferred) * self.config['skills_config']['nice_to_have_factor'])) / total_skills
        else:
            score = required_score
        
        return score
    
    def _get_matched_skills(self, candidate_skills: List[str], job_skills: List[str]) -> set:
        """
        Identifier les compétences correspondantes avec gestion des synonymes
        et variantes technologiques
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences du poste
            
        Returns:
            set: Ensemble des compétences correspondantes
        """
        # Pour le MVP, on utilise une correspondance simple
        # À l'avenir: intégrer des synonymes et des relations entre technologies
        return set(candidate_skills).intersection(set(job_skills))
    
    def _calculate_experience_match(self, candidate_experience: str, required_experience: str) -> float:
        """
        Calculer la correspondance d'expérience avec courbe de valorisation
        
        Args:
            candidate_experience: Expérience du candidat
            required_experience: Expérience requise pour le poste
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        try:
            # Extraction des années d'expérience
            candidate_years = self._extract_years_from_experience(candidate_experience)
            min_years, max_years = self._extract_min_max_years(required_experience)
            
            if candidate_years is None or min_years is None:
                return 0.5  # Score neutre si données manquantes
            
            # Nouvelle logique de scoring avec courbe de valorisation
            if candidate_years < min_years:
                # Expérience insuffisante - courbe non linéaire
                ratio = candidate_years / min_years if min_years > 0 else 0
                # Formule qui pénalise moins les écarts mineurs
                score = max(0, ratio ** 0.8)  
            elif max_years is not None and candidate_years > max_years * 1.5:
                # Très surqualifié - légère pénalité
                score = 0.85
            elif max_years is not None and candidate_years > max_years:
                # Légèrement surqualifié - quasi idéal
                score = 0.95
            else:
                # Expérience dans la fourchette - idéal
                score = 1.0
            
            return score
        except Exception as e:
            # Gestion d'erreur
            logger.error(f"Erreur lors du calcul de la correspondance d'expérience: {str(e)}", exc_info=True)
            return 0.5
    
    def _extract_years_from_experience(self, experience_text: str) -> Optional[int]:
        """
        Extraire le nombre d'années d'expérience à partir d'un texte
        
        Args:
            experience_text: Texte décrivant l'expérience (ex: "5 ans")
            
        Returns:
            int ou None: Nombre d'années d'expérience ou None si non détecté
        """
        if not experience_text or experience_text == "Non détecté":
            return None
        
        # Recherche de motifs comme "5 ans", "5+ ans", "cinq ans", etc.
        pattern = r'(\d+)(?:\+)?\\s*(?:an|ans|années)'
        match = re.search(pattern, experience_text.lower())
        
        if match:
            return int(match.group(1))
        
        # Conversion de texte en nombre pour les cas comme "cinq ans"
        number_words = {
            'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
            'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10
        }
        
        for word, value in number_words.items():
            if f"{word} an" in experience_text.lower() or f"{word} ans" in experience_text.lower():
                return value
        
        return None
    
    def _extract_min_max_years(self, required_experience: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Extraire l'expérience minimale et maximale requise
        
        Args:
            required_experience: Texte décrivant l'expérience requise (ex: "3-5 ans")
            
        Returns:
            tuple: (min_years, max_years) ou (min_years, None) si pas de maximum
        """
        if not required_experience:
            return None, None
        
        # Recherche de motifs comme "3-5 ans", "minimum 3 ans", "au moins 3 ans", etc.
        range_pattern = r'(\d+)\\s*-\\s*(\d+)\\s*(?:an|ans|années)'
        min_pattern = r'(?:minimum|min|au moins)\\s*(\d+)\\s*(?:an|ans|années)'
        single_pattern = r'(\d+)\\s*(?:an|ans|années)'
        
        # Vérifier d'abord s'il y a une fourchette
        range_match = re.search(range_pattern, required_experience.lower())
        if range_match:
            return int(range_match.group(1)), int(range_match.group(2))
        
        # Vérifier s'il y a un minimum explicite
        min_match = re.search(min_pattern, required_experience.lower())
        if min_match:
            return int(min_match.group(1)), None
        
        # Vérifier s'il y a juste un nombre
        single_match = re.search(single_pattern, required_experience.lower())
        if single_match:
            return int(single_match.group(1)), int(single_match.group(1))
        
        return None, None
    
    def _calculate_description_match(self, candidate_description: str, job_description: str) -> float:
        """
        Calculer la correspondance entre la description du profil et celle du poste
        
        Args:
            candidate_description: Description du profil ou résumé du CV
            job_description: Description du poste
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        if not candidate_description or not job_description:
            return 0.5  # Score neutre si les données sont manquantes
        
        try:
            # Extraction des mots-clés des descriptions
            candidate_keywords = self._extract_keywords(candidate_description)
            job_keywords = self._extract_keywords(job_description)
            
            # Calcul de la similarité entre les descriptions
            similarity_score = self._calculate_text_similarity(candidate_keywords, job_keywords)
            
            return similarity_score
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la correspondance de description: {str(e)}", exc_info=True)
            return 0.5  # Score neutre en cas d'erreur
    
    def _calculate_title_match(self, candidate_title: str, job_title: str) -> float:
        """
        Calculer la correspondance des titres de poste
        
        Args:
            candidate_title: Titre du poste du candidat
            job_title: Titre du poste de l'offre
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        if not candidate_title or not job_title:
            return 0.5  # Score neutre si les données sont manquantes
        
        # Normalisation des titres
        normalized_candidate_title = self._normalize_text(candidate_title)
        normalized_job_title = self._normalize_text(job_title)
        
        # Comparaison directe
        if normalized_candidate_title == normalized_job_title:
            return 1.0
        
        # Similarité basée sur les mots communs
        candidate_words = set(normalized_candidate_title.split())
        job_words = set(normalized_job_title.split())
        
        common_words = candidate_words.intersection(job_words)
        
        if not common_words:
            return 0.3  # Score minimum pour les titres sans mots communs
        
        similarity = len(common_words) / max(len(candidate_words), len(job_words))
        
        return similarity
    
    def _calculate_questionnaire_match(self, candidate_questionnaire: Dict[str, Any], 
                                      company_questionnaire: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculer la correspondance entre les réponses aux questionnaires
        
        Args:
            candidate_questionnaire: Réponses du candidat au questionnaire
            company_questionnaire: Réponses de l'entreprise au questionnaire
            
        Returns:
            dict: Scores de correspondance par section et score total
        """
        if not candidate_questionnaire or not company_questionnaire:
            return {
                'total': 0.5,  # Score neutre si questionnaires non remplis
                'informations_personnelles': 0.5,
                'mobilite_preferences': 0.5,
                'motivations_secteurs': 0.5,
                'disponibilite_situation': 0.5
            }
        
        # Calcul des scores par section
        scores = {
            'informations_personnelles': self._compare_personal_info(candidate_questionnaire, company_questionnaire),
            'mobilite_preferences': self._compare_mobility_preferences(candidate_questionnaire, company_questionnaire),
            'motivations_secteurs': self._compare_motivations_sectors(candidate_questionnaire, company_questionnaire),
            'disponibilite_situation': self._compare_availability_situation(candidate_questionnaire, company_questionnaire)
        }
        
        # Calcul du score total du questionnaire (moyenne pondérée)
        weights = self.config['weights']
        total_questionnaire_weight = sum([
            weights['informations_personnelles'],
            weights['mobilite_preferences'],
            weights['motivations_secteurs'],
            weights['disponibilite_situation']
        ])
        
        scores['total'] = (
            scores['informations_personnelles'] * weights['informations_personnelles'] +
            scores['mobilite_preferences'] * weights['mobilite_preferences'] +
            scores['motivations_secteurs'] * weights['motivations_secteurs'] +
            scores['disponibilite_situation'] * weights['disponibilite_situation']
        ) / total_questionnaire_weight
        
        return scores
    
    def _compare_personal_info(self, candidate_questionnaire: Dict[str, Any], 
                              company_questionnaire: Dict[str, Any]) -> float:
        """
        Comparer la section "Informations personnelles"
        
        Args:
            candidate_questionnaire: Réponses du candidat
            company_questionnaire: Réponses de l'entreprise
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        score = 0.5  # Score par défaut
        
        # Comparaison du poste souhaité avec le poste proposé
        candidate_job_title = self._get_questionnaire_value(candidate_questionnaire, 'poste_souhaite', '')
        company_job_title = self._get_questionnaire_value(company_questionnaire, 'poste_propose', '')
        
        if candidate_job_title and company_job_title:
            # Utiliser la similarité des titres de poste
            title_similarity = self._calculate_title_similarity(candidate_job_title, company_job_title)
            score = title_similarity
        
        return score
    
    def _compare_mobility_preferences(self, candidate_questionnaire: Dict[str, Any], 
                                     company_questionnaire: Dict[str, Any]) -> float:
        """
        Comparer la section "Mobilité et préférences"
        
        Args:
            candidate_questionnaire: Réponses du candidat
            company_questionnaire: Réponses de l'entreprise
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Initialisations
        score_components = []
        
        # 1. Correspondance du mode de travail
        candidate_work_mode = self._get_questionnaire_value(candidate_questionnaire, 'mode_travail', '')
        company_work_mode = self._get_questionnaire_value(company_questionnaire, 'mode_travail', '')
        
        if candidate_work_mode and company_work_mode:
            if candidate_work_mode == company_work_mode:
                score_components.append(1.0)
            elif (candidate_work_mode == "Hybride" and company_work_mode in ["Sur site", "Full remote"]) or \
                 (company_work_mode == "Hybride" and candidate_work_mode in ["Sur site", "Full remote"]):
                score_components.append(0.7)  # Correspondance partielle
            else:
                score_components.append(0.3)  # Faible correspondance
        
        # 2. Correspondance de localisation
        candidate_location = self._get_questionnaire_value(candidate_questionnaire, 'localisation', '')
        company_location = self._get_questionnaire_value(company_questionnaire, 'localisation', '')
        
        if candidate_location and company_location:
            if candidate_location == company_location:
                score_components.append(1.0)
            else:
                # Logique à développer pour la proximité géographique
                score_components.append(0.5)
        
        # 3. Correspondance du type de contrat
        candidate_contract = self._get_questionnaire_value(candidate_questionnaire, 'type_contrat', '')
        company_contract = self._get_questionnaire_value(company_questionnaire, 'type_contrat', '')
        
        if candidate_contract and company_contract:
            if candidate_contract == company_contract:
                score_components.append(1.0)
            else:
                score_components.append(0.2)  # Forte pénalité pour un mauvais type de contrat
        
        # 4. Correspondance de la taille d'entreprise
        candidate_company_size = self._get_questionnaire_value(candidate_questionnaire, 'taille_entreprise', '')
        company_size = self._get_questionnaire_value(company_questionnaire, 'taille_entreprise', '')
        
        if candidate_company_size and company_size:
            if candidate_company_size == company_size or candidate_company_size == "Peu importe":
                score_components.append(1.0)
            else:
                score_components.append(0.6)  # Pénalité modérée
        
        # Calcul du score global de cette section
        if score_components:
            return sum(score_components) / len(score_components)
        else:
            return 0.5  # Score par défaut si aucune donnée
    
    def _compare_motivations_sectors(self, candidate_questionnaire: Dict[str, Any], 
                                    company_questionnaire: Dict[str, Any]) -> float:
        """
        Comparer la section "Motivations et secteurs"
        
        Args:
            candidate_questionnaire: Réponses du candidat
            company_questionnaire: Réponses de l'entreprise
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Initialisations
        score_components = []
        
        # 1. Correspondance des secteurs d'activité
        candidate_sectors = self._get_questionnaire_value(candidate_questionnaire, 'secteurs', [])
        company_sector = self._get_questionnaire_value(company_questionnaire, 'secteur', '')
        
        if candidate_sectors and company_sector:
            if company_sector in candidate_sectors:
                score_components.append(1.0)
            else:
                score_components.append(0.4)  # Pénalité modérée
        
        # 2. Correspondance des valeurs d'entreprise
        candidate_values = self._get_questionnaire_value(candidate_questionnaire, 'valeurs', [])
        company_values = self._get_questionnaire_value(company_questionnaire, 'valeurs', [])
        
        if candidate_values and company_values:
            common_values = set(candidate_values).intersection(set(company_values))
            if common_values:
                score_components.append(len(common_values) / len(company_values))
            else:
                score_components.append(0.4)  # Pénalité modérée
        
        # 3. Correspondance des technologies
        candidate_technologies = self._get_questionnaire_value(candidate_questionnaire, 'technologies', [])
        company_technologies = self._get_questionnaire_value(company_questionnaire, 'technologies', [])
        
        if candidate_technologies and company_technologies:
            common_technologies = set(candidate_technologies).intersection(set(company_technologies))
            required_technologies = self._get_questionnaire_value(company_questionnaire, 'technologies_requises', [])
            
            # Vérifier les technologies requises
            if required_technologies:
                required_match = all(tech in candidate_technologies for tech in required_technologies)
                if required_match:
                    score_components.append(1.0)
                else:
                    score_components.append(0.2)  # Forte pénalité
            else:
                # Correspondance basée sur le nombre de technologies communes
                if common_technologies:
                    score_components.append(len(common_technologies) / len(company_technologies))
                else:
                    score_components.append(0.4)
        
        # Calcul du score global de cette section
        if score_components:
            return sum(score_components) / len(score_components)
        else:
            return 0.5  # Score par défaut si aucune donnée
    
    def _compare_availability_situation(self, candidate_questionnaire: Dict[str, Any], 
                                       company_questionnaire: Dict[str, Any]) -> float:
        """
        Comparer la section "Disponibilité et situation"
        
        Args:
            candidate_questionnaire: Réponses du candidat
            company_questionnaire: Réponses de l'entreprise
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Initialisations
        score_components = []
        
        # 1. Correspondance de disponibilité
        candidate_availability = self._get_questionnaire_value(candidate_questionnaire, 'disponibilite', '')
        company_start_date = self._get_questionnaire_value(company_questionnaire, 'date_debut', '')
        
        if candidate_availability and company_start_date:
            # Logique à développer pour comparer les dates
            # Pour le MVP, considérons une correspondance simple
            score_components.append(0.8)  # Valeur arbitraire pour le MVP
        
        # 2. Correspondance des attentes salariales
        candidate_salary = self._get_questionnaire_value(candidate_questionnaire, 'salaire', {})
        company_salary = self._get_questionnaire_value(company_questionnaire, 'salaire', {})
        
        if candidate_salary and company_salary:
            # Extraction des fourchettes
            candidate_min = candidate_salary.get('min', 0)
            candidate_max = candidate_salary.get('max', 0)
            company_min = company_salary.get('min', 0)
            company_max = company_salary.get('max', 0)
            
            # Cas de non-intersection
            if candidate_min > company_max or candidate_max < company_min:
                score_components.append(0.2)  # Forte pénalité
            # Intersection partielle
            elif candidate_min < company_min or candidate_max > company_max:
                score_components.append(0.7)  # Légère pénalité
            # Correspondance parfaite
            else:
                score_components.append(1.0)
        
        # Calcul du score global de cette section
        if score_components:
            return sum(score_components) / len(score_components)
        else:
            return 0.5  # Score par défaut si aucune donnée
    
    def _generate_match_insights(self, candidate_data: Dict[str, Any], 
                                job_data: Dict[str, Any], 
                                total_score: float,
                                questionnaire_scores: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Générer des insights sur les forces et les points d'amélioration du matching
        
        Args:
            candidate_data: Données du candidat
            job_data: Données de l'offre
            total_score: Score global du matching
            questionnaire_scores: Scores des différentes sections du questionnaire
            
        Returns:
            dict: Insights classés par catégorie
        """
        insights = {
            'strengths': [],
            'areas_of_improvement': [],
            'recommendations': []
        }
        
        # Analyse des questionnaires
        candidate_questionnaire = candidate_data.get('questionnaire', {})
        company_questionnaire = job_data.get('questionnaire', {})
        
        # Extraction des forces (scores élevés)
        if questionnaire_scores['mobilite_preferences'] >= 0.8:
            insights['strengths'].append("Excellente adéquation des préférences de travail")
        
        if questionnaire_scores['motivations_secteurs'] >= 0.8:
            insights['strengths'].append("Fort intérêt pour le secteur d'activité")
        
        # Extraction des points d'amélioration (scores faibles)
        if questionnaire_scores['mobilite_preferences'] < 0.4:
            # Vérifier la cause spécifique
            candidate_work_mode = self._get_questionnaire_value(candidate_questionnaire, 'mode_travail', '')
            company_work_mode = self._get_questionnaire_value(company_questionnaire, 'mode_travail', '')
            
            if candidate_work_mode != company_work_mode:
                insights['areas_of_improvement'].append(f"Préférence pour {candidate_work_mode} vs {company_work_mode} requis")
        
        # Recommendations basées sur le score global
        if total_score >= 0.85:
            insights['recommendations'].append("Profil très adapté, à contacter en priorité")
        elif total_score >= 0.7:
            insights['recommendations'].append("Bon profil, entretien recommandé")
        elif total_score >= 0.5:
            insights['recommendations'].append("Profil intéressant mais avec quelques écarts, à évaluer")
        else:
            insights['recommendations'].append("Correspondance limitée avec le poste")
        
        return insights
    
    def _get_questionnaire_value(self, questionnaire: Dict[str, Any], 
                                field_id: str, 
                                default: Any = None) -> Any:
        """
        Récupérer une valeur dans le questionnaire
        
        Args:
            questionnaire: Données du questionnaire
            field_id: Identifiant du champ
            default: Valeur par défaut si le champ n'existe pas
            
        Returns:
            Any: Valeur du champ ou valeur par défaut
        """
        # Pour le MVP: structure simple
        return questionnaire.get(field_id, default)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliser un texte (mise en minuscules, suppression d'accents, etc.)
        
        Args:
            text: Texte à normaliser
            
        Returns:
            str: Texte normalisé
        """
        if not text:
            return ""
        # Pour le MVP: simple mise en minuscules et suppression de caractères spéciaux
        return re.sub(r'[^\w\s]', '', text.lower())
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extraire les mots-clés d'un texte
        
        Args:
            text: Texte source
            
        Returns:
            list: Liste des mots-clés extraits
        """
        if not text:
            return []
        # Pour le MVP: simple division en mots
        # À améliorer: extraction de mots-clés avec TF-IDF ou modèles NLP
        words = text.lower().split()
        # Filtrer les mots vides et trop courts
        return [w for w in words if len(w) > 3]
    
    def _calculate_text_similarity(self, text1: List[str], text2: List[str]) -> float:
        """
        Calculer la similarité entre deux ensembles de texte
        
        Args:
            text1: Premier ensemble de texte
            text2: Deuxième ensemble de texte
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        if not text1 or not text2:
            return 0
        
        # Pour le MVP: similarité de Jaccard
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0
        
        return intersection / union
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculer la similarité entre deux titres de poste
        
        Args:
            title1: Premier titre
            title2: Deuxième titre
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Normalisation
        normalized_title1 = self._normalize_text(title1)
        normalized_title2 = self._normalize_text(title2)
        
        # Comparaison directe
        if normalized_title1 == normalized_title2:
            return 1.0
        
        # Comparaison basée sur les mots
        words1 = set(normalized_title1.split())
        words2 = set(normalized_title2.split())
        
        common_words = words1.intersection(words2)
        
        if not common_words:
            return 0.3
        
        # Calcul de la similarité de Jaccard
        return len(common_words) / len(words1.union(words2))
    
    def _classify_match(self, score: float) -> str:
        """
        Classifier le match selon son score
        
        Args:
            score: Score de correspondance
            
        Returns:
            str: Catégorie du match
        """
        if score >= self.config['thresholds']['excellent_match']:
            return "excellent"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "moderate"
        elif score >= self.config['thresholds']['minimum_score']:
            return "low"
        else:
            return "insufficient"


# Point d'entrée simple pour les opérations de matching
def match_candidate_to_job(candidate: Dict[str, Any], job: Dict[str, Any], 
                          config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Point d'entrée simple pour calculer la correspondance entre un candidat et une offre
    
    Args:
        candidate: Données du candidat
        job: Données de l'offre d'emploi
        config: Configuration personnalisée de l'algorithme
        
    Returns:
        dict: Résultat du matching
    """
    matcher = NextenMatchingAlgorithm(config)
    result = matcher.calculate_match(candidate, job)
    
    return {
        'candidate_id': candidate.get('id'),
        'job_id': job.get('id'),
        'matching_score': result['score'],
        'matching_category': result['category'],
        'details': result['details'],
        'insights': result['insights']
    }

def match_candidate_to_multiple_jobs(candidate: Dict[str, Any], 
                                   jobs: List[Dict[str, Any]],
                                   config: Optional[Dict[str, Any]] = None,
                                   min_score: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Calculer la correspondance entre un candidat et plusieurs offres
    
    Args:
        candidate: Données du candidat
        jobs: Liste des offres d'emploi
        config: Configuration personnalisée
        min_score: Score minimum pour inclure un match
        
    Returns:
        list: Liste des correspondances triées par score
    """
    matcher = NextenMatchingAlgorithm(config)
    results = []
    
    for job in jobs:
        result = matcher.calculate_match(candidate, job)
        
        # Filtrer selon le score minimum si défini
        if min_score is not None and result['score'] < min_score:
            continue
            
        results.append({
            'candidate_id': candidate.get('id'),
            'job_id': job.get('id'),
            'job_title': job.get('title'),
            'company': job.get('company'),
            'matching_score': result['score'],
            'matching_category': result['category'],
            'details': result['details'],
            'insights': result['insights']
        })
    
    # Trier par score décroissant
    return sorted(results, key=lambda x: x['matching_score'], reverse=True)

def match_job_to_multiple_candidates(job: Dict[str, Any], 
                                   candidates: List[Dict[str, Any]],
                                   config: Optional[Dict[str, Any]] = None,
                                   min_score: Optional[float] = None,
                                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Calculer la correspondance entre une offre et plusieurs candidats
    
    Args:
        job: Données de l'offre d'emploi
        candidates: Liste des candidats
        config: Configuration personnalisée
        min_score: Score minimum pour inclure un match
        limit: Nombre maximum de résultats à retourner
        
    Returns:
        list: Liste des correspondances triées par score
    """
    matcher = NextenMatchingAlgorithm(config)
    results = []
    
    for candidate in candidates:
        result = matcher.calculate_match(candidate, job)
        
        # Filtrer selon le score minimum si défini
        if min_score is not None and result['score'] < min_score:
            continue
            
        results.append({
            'candidate_id': candidate.get('id'),
            'candidate_name': candidate.get('name'),
            'job_id': job.get('id'),
            'matching_score': result['score'],
            'matching_category': result['category'],
            'details': result['details'],
            'insights': result['insights']
        })
    
    # Trier par score décroissant
    sorted_results = sorted(results, key=lambda x: x['matching_score'], reverse=True)
    
    # Limiter le nombre de résultats si demandé
    if limit is not None and isinstance(limit, int) and limit > 0:
        return sorted_results[:limit]
        
    return sorted_results
