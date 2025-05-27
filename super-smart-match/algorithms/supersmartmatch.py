#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch Algorithm - Algorithme intelligent avec matching côté entreprise
Calcule des pourcentages de correspondance précis sur :
- Localisation (temps de trajet)
- Expérience
- Rémunération
- Compétences (langues, logiciels)
- Raisonnement intelligent (évolution rapide, perspectives, etc.)
"""

import sys
import os
import logging
import math
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from .base import BaseAlgorithm

logger = logging.getLogger(__name__)

class SuperSmartMatchAlgorithm(BaseAlgorithm):
    """
    Algorithme SuperSmartMatch avec intelligence artificielle pour le matching côté entreprise
    """
    
    def __init__(self):
        super().__init__()
        self.name = "supersmartmatch"
        self.description = "Algorithme intelligent avec pourcentages côté entreprise et raisonnement avancé"
        self.version = "2.0"
        self.initialized = True
        
        # Configuration des seuils intelligents
        self.config = {
            'seuils': {
                'localisation': {
                    'excellent': 85,    # Même ville/quartier
                    'bon': 70,         # Même région, <30min transport
                    'acceptable': 50,   # <1h transport
                    'limite': 30       # >1h transport
                },
                'experience': {
                    'parfait': 90,     # Expérience exacte
                    'superieur': 95,   # Surqualifié modéré
                    'acceptable': 75,  # Légèrement sous-qualifié
                    'junior': 60       # Junior avec potentiel
                },
                'remuneration': {
                    'ideal': 95,       # Dans la fourchette
                    'negotiable': 80,  # Écart <20%
                    'risque': 60,      # Écart 20-40%
                    'difficile': 30    # Écart >40%
                },
                'competences': {
                    'expert': 95,      # Toutes compétences + bonus
                    'competent': 85,   # Toutes compétences requises
                    'partiel': 70,     # 80% des compétences
                    'apprentissage': 50 # 60% + potentiel d'apprentissage
                }
            },
            'ponderation': {
                'localisation': 0.25,
                'experience': 0.25, 
                'remuneration': 0.20,
                'competences': 0.30
            },
            'bonus_intelligence': {
                'evolution_rapide': 10,     # Candidat ambitieux + poste évolutif
                'stabilite': 8,             # Candidat stable + poste long terme
                'innovation': 12,           # Candidat créatif + environnement innovant
                'leadership': 15,           # Potentiel management + responsabilités
                'specialisation': 10,       # Expert technique + poste technique
                'adaptabilite': 8           # Polyvalent + environnement changeant
            }
        }
    
    def supports(self, candidat: Dict[str, Any], offres: List[Dict[str, Any]]) -> bool:
        """
        SuperSmartMatch peut traiter tous types de données
        """
        return True
    
    def match_candidate_with_jobs(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute le matching SuperSmartMatch intelligent côté entreprise
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des offres avec scores de matching détaillés
        """
        logger.info(f"Démarrage SuperSmartMatch pour {len(offres)} offres")
        
        results = []
        candidat_profile = self._analyze_candidate_profile(candidat)
        
        for i, offre in enumerate(offres[:limit]):
            try:
                # Calcul des scores détaillés
                scores = self._calculate_detailed_scores(candidat, offre, candidat_profile)
                
                # Application du raisonnement intelligent
                intelligence_bonus = self._apply_intelligent_reasoning(candidat, offre, candidat_profile)
                
                # Score final avec bonus intelligence
                final_score = self._calculate_final_score(scores, intelligence_bonus)
                
                # Génération des explications intelligentes
                explanations = self._generate_intelligent_explanations(
                    candidat, offre, scores, intelligence_bonus, candidat_profile
                )
                
                result = {
                    'id': offre.get('id', f'job_{i}'),
                    'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                    'entreprise': offre.get('entreprise', 'Entreprise non spécifiée'),
                    
                    # Score principal (côté entreprise)
                    'matching_score_entreprise': int(final_score),
                    
                    # Détails des scores par critère (côté entreprise)
                    'scores_detailles': {
                        'localisation': {
                            'pourcentage': int(scores['localisation']),
                            'details': scores['localisation_details']
                        },
                        'experience': {
                            'pourcentage': int(scores['experience']),
                            'details': scores['experience_details']
                        },
                        'remuneration': {
                            'pourcentage': int(scores['remuneration']),
                            'details': scores['remuneration_details']
                        },
                        'competences': {
                            'pourcentage': int(scores['competences']),
                            'details': scores['competences_details']
                        }
                    },
                    
                    # Raisonnement intelligent appliqué
                    'intelligence': {
                        'bonus_applique': intelligence_bonus['total'],
                        'raisons': intelligence_bonus['raisons'],
                        'recommandations': intelligence_bonus['recommandations']
                    },
                    
                    # Explications détaillées pour l'entreprise
                    'explications_entreprise': explanations,
                    
                    # Risques et opportunités
                    'analyse_risques': self._analyze_risks_opportunities(candidat, offre),
                    
                    # Profil candidat pour l'entreprise
                    'profil_candidat': candidat_profile,
                    
                    **offre  # Inclure toutes les données de l'offre originale
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'offre {i}: {e}")
                # Fallback avec score basique
                result = self._create_fallback_result(candidat, offre, i)
                results.append(result)
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['matching_score_entreprise'], reverse=True)
        
        logger.info(f"SuperSmartMatch terminé - {len(results)} résultats générés")
        return results
    
    def _analyze_candidate_profile(self, candidat: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse le profil du candidat pour identifier ses caractéristiques clés
        """
        profile = {
            'type_profil': 'standard',
            'niveau_experience': 'moyen',
            'ambition': 'moyenne',
            'stabilite': 'moyenne',
            'specialisation': [],
            'points_forts': [],
            'potentiel_evolution': 'moyen'
        }
        
        # Analyser l'expérience
        experience = candidat.get('annees_experience', 0)
        if experience <= 2:
            profile['niveau_experience'] = 'junior'
            profile['potentiel_evolution'] = 'élevé'
        elif experience <= 5:
            profile['niveau_experience'] = 'moyen'
        elif experience <= 10:
            profile['niveau_experience'] = 'senior'
        else:
            profile['niveau_experience'] = 'expert'
            profile['specialisation'] = candidat.get('competences', [])[:3]  # Top 3 compétences
        
        # Analyser l'ambition (basé sur les critères et objectifs)
        criteres = candidat.get('criteres_importants', {})
        objectifs = candidat.get('objectifs_carriere', {})
        
        if (objectifs.get('evolution_rapide') or 
            criteres.get('responsabilites_importantes') or
            candidat.get('leadership_experience')):
            profile['ambition'] = 'élevée'
            profile['type_profil'] = 'ambitieux'
        
        # Analyser la stabilité
        mobilite = candidat.get('mobilite', '')
        duree_poste_souhaite = candidat.get('duree_poste_souhaite', '')
        
        if ('long terme' in duree_poste_souhaite.lower() or 
            'stabilité' in criteres.get('priorites', [])):
            profile['stabilite'] = 'élevée'
            profile['type_profil'] = 'stable'
        
        # Identifier les points forts
        competences = candidat.get('competences', [])
        langues = candidat.get('langues', [])
        soft_skills = candidat.get('soft_skills', [])
        
        if len(competences) >= 8:
            profile['points_forts'].append('polyvalent')
        if len(langues) >= 2:
            profile['points_forts'].append('international')
        if any('management' in skill.lower() or 'leadership' in skill.lower() 
               for skill in soft_skills):
            profile['points_forts'].append('leadership')
        
        return profile
    
    def _calculate_detailed_scores(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any],
        candidat_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule les scores détaillés pour chaque critère côté entreprise
        """
        scores = {}
        
        # 1. LOCALISATION - Temps de trajet et mobilité
        scores.update(self._calculate_location_score_detailed(candidat, offre))
        
        # 2. EXPÉRIENCE - Adéquation niveau/poste
        scores.update(self._calculate_experience_score_detailed(candidat, offre, candidat_profile))
        
        # 3. RÉMUNÉRATION - Compatibilité budget entreprise
        scores.update(self._calculate_salary_score_detailed(candidat, offre))
        
        # 4. COMPÉTENCES - Techniques, langues, logiciels
        scores.update(self._calculate_skills_score_detailed(candidat, offre))
        
        return scores
    
    def _calculate_location_score_detailed(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule le score de localisation avec estimation du temps de trajet
        """
        candidat_location = candidat.get('adresse', '').lower().strip()
        job_location = offre.get('localisation', '').lower().strip()
        mobilite = candidat.get('mobilite', '').lower()
        remote_policy = offre.get('politique_remote', '').lower()
        
        score = 50  # Score de base
        details = []
        
        # Si télétravail possible
        if 'télétravail' in remote_policy or 'remote' in remote_policy:
            if 'télétravail' in mobilite or candidat.get('preferences_remote', False):
                score = 95
                details.append("Télétravail compatible - Excellent match")
            else:
                score = 85
                details.append("Télétravail possible mais candidat préfère présentiel")
        
        # Analyse géographique
        elif candidat_location and job_location:
            # Correspondance exacte de ville
            if candidat_location in job_location or job_location in candidat_location:
                score = 90
                details.append("Même ville - Trajet court")
            
            # Correspondance région/département
            elif self._same_region(candidat_location, job_location):
                score = 75
                details.append("Même région - Trajet acceptable (30-45min)")
            
            # Villes différentes
            else:
                distance_km = self._estimate_distance(candidat_location, job_location)
                if distance_km <= 30:
                    score = 70
                    details.append(f"Distance estimée: {distance_km}km - Trajet acceptable")
                elif distance_km <= 50:
                    score = 55
                    details.append(f"Distance estimée: {distance_km}km - Trajet long (1h+)")
                else:
                    score = 35
                    details.append(f"Distance estimée: {distance_km}km - Trajet très long")
        
        # Bonus mobilité
        if 'mobile' in mobilite or 'disponible' in mobilite:
            score = min(100, score + 10)
            details.append("Candidat mobile - Bonus flexibilité")
        
        return {
            'localisation': score,
            'localisation_details': details
        }
    
    def _calculate_experience_score_detailed(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any],
        candidat_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule le score d'expérience avec analyse de l'adéquation
        """
        candidat_exp = candidat.get('annees_experience', 0)
        required_exp = offre.get('experience_requise', 0)
        niveau_poste = offre.get('niveau_poste', '').lower()
        
        score = 50
        details = []
        
        if required_exp == 0:
            score = 85
            details.append("Aucune expérience requise - Poste ouvert")
        else:
            # Calcul basé sur l'adéquation
            ratio = candidat_exp / required_exp if required_exp > 0 else 1
            
            if ratio >= 1.0 and ratio <= 1.5:
                # Expérience parfaite
                score = 95
                details.append(f"Expérience parfaite: {candidat_exp} ans pour {required_exp} ans requis")
            
            elif ratio > 1.5 and ratio <= 2.0:
                # Légèrement surqualifié
                score = 90
                details.append(f"Légèrement surqualifié: {candidat_exp} ans pour {required_exp} ans requis")
            
            elif ratio > 2.0:
                # Très surqualifié - risque de départ
                score = 75
                details.append(f"Surqualifié: {candidat_exp} ans pour {required_exp} ans requis - Risque d'ennui")
            
            elif ratio >= 0.8:
                # Légèrement sous-qualifié mais acceptable
                score = 80
                details.append(f"Légèrement sous-qualifié mais expérience proche: {candidat_exp}/{required_exp} ans")
            
            elif ratio >= 0.5:
                # Sous-qualifié mais potentiel
                if candidat_profile['potentiel_evolution'] == 'élevé':
                    score = 70
                    details.append(f"Sous-qualifié mais fort potentiel: {candidat_exp}/{required_exp} ans")
                else:
                    score = 60
                    details.append(f"Sous-qualifié: {candidat_exp}/{required_exp} ans")
            
            else:
                # Très sous-qualifié
                score = 40
                details.append(f"Expérience insuffisante: {candidat_exp}/{required_exp} ans")
        
        # Bonus selon le type de profil
        if 'senior' in niveau_poste and candidat_profile['niveau_experience'] == 'expert':
            score = min(100, score + 10)
            details.append("Profil senior pour poste senior - Bonus expérience")
        
        return {
            'experience': score,
            'experience_details': details
        }
    
    def _calculate_salary_score_detailed(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule le score de rémunération du point de vue entreprise
        """
        candidat_salary = candidat.get('salaire_souhaite', 0)
        job_salary_str = offre.get('salaire', '').lower()
        budget_max = offre.get('budget_max', 0)
        
        score = 70  # Score neutre si pas d'info
        details = []
        
        if not candidat_salary:
            score = 70
            details.append("Prétentions salariales non spécifiées - À négocier")
            return {'remuneration': score, 'remuneration_details': details}
        
        # Parser le budget de l'offre
        salary_range = self._parse_salary_range(job_salary_str, budget_max)
        
        if not salary_range:
            score = 70
            details.append(f"Candidat demande {candidat_salary}€ - Budget offre à préciser")
            return {'remuneration': score, 'remuneration_details': details}
        
        min_salary, max_salary = salary_range
        
        # Analyse côté entreprise
        if candidat_salary <= min_salary:
            # Candidat demande moins que le minimum - Excellent pour l'entreprise
            economy = ((min_salary - candidat_salary) / min_salary) * 100
            score = 98
            details.append(f"Candidat sous le budget minimum - Économie de {economy:.0f}%")
        
        elif candidat_salary <= max_salary:
            # Dans la fourchette - Parfait
            position = ((candidat_salary - min_salary) / (max_salary - min_salary)) * 100
            score = 95
            details.append(f"Dans la fourchette budgétaire ({position:.0f}% de la fourchette)")
        
        elif candidat_salary <= max_salary * 1.1:
            # Légèrement au-dessus - Négociable
            excess = ((candidat_salary - max_salary) / max_salary) * 100
            score = 80
            details.append(f"Légèrement au-dessus du budget (+{excess:.0f}%) - Négociable")
        
        elif candidat_salary <= max_salary * 1.2:
            # 20% au-dessus - Difficile mais possible
            excess = ((candidat_salary - max_salary) / max_salary) * 100
            score = 60
            details.append(f"Au-dessus du budget (+{excess:.0f}%) - Négociation difficile")
        
        else:
            # Trop cher
            excess = ((candidat_salary - max_salary) / max_salary) * 100
            score = 30
            details.append(f"Hors budget (+{excess:.0f}%) - Très difficile à recruter")
        
        return {
            'remuneration': score,
            'remuneration_details': details
        }
    
    def _calculate_skills_score_detailed(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule le score de compétences détaillé (techniques, langues, logiciels)
        """
        # Compétences techniques
        candidat_skills = set(skill.lower().strip() for skill in candidat.get('competences', []))
        required_skills = set(skill.lower().strip() for skill in offre.get('competences', []))
        
        # Langues
        candidat_langues = candidat.get('langues', [])
        required_langues = offre.get('langues_requises', [])
        
        # Logiciels
        candidat_logiciels = candidat.get('logiciels', [])
        required_logiciels = offre.get('logiciels_requis', [])
        
        scores_detail = {}
        details = []
        
        # 1. Compétences techniques (40% du score compétences)
        if required_skills:
            matching_skills = candidat_skills.intersection(required_skills)
            missing_skills = required_skills - candidat_skills
            bonus_skills = candidat_skills - required_skills
            
            coverage = len(matching_skills) / len(required_skills)
            tech_score = coverage * 100
            
            # Bonus pour compétences supplémentaires
            if bonus_skills:
                bonus = min(15, len(bonus_skills) * 3)
                tech_score = min(100, tech_score + bonus)
            
            scores_detail['techniques'] = tech_score
            details.append(f"Compétences techniques: {len(matching_skills)}/{len(required_skills)} requises")
            
            if missing_skills:
                details.append(f"Manquantes: {', '.join(list(missing_skills)[:3])}")
            if bonus_skills:
                details.append(f"Bonus: {', '.join(list(bonus_skills)[:3])}")
        else:
            scores_detail['techniques'] = 80
            details.append("Compétences techniques: Aucune exigence spécifique")
        
        # 2. Langues (30% du score compétences)
        if required_langues:
            candidat_langues_set = set(lang.lower() for lang in candidat_langues)
            required_langues_set = set(lang.lower() for lang in required_langues)
            
            matching_langues = candidat_langues_set.intersection(required_langues_set)
            langues_score = (len(matching_langues) / len(required_langues_set)) * 100
            
            scores_detail['langues'] = langues_score
            details.append(f"Langues: {len(matching_langues)}/{len(required_langues)} requises")
        else:
            scores_detail['langues'] = 85
            details.append("Langues: Aucune exigence")
        
        # 3. Logiciels (30% du score compétences)
        if required_logiciels:
            candidat_logiciels_set = set(log.lower() for log in candidat_logiciels)
            required_logiciels_set = set(log.lower() for log in required_logiciels)
            
            matching_logiciels = candidat_logiciels_set.intersection(required_logiciels_set)
            logiciels_score = (len(matching_logiciels) / len(required_logiciels_set)) * 100
            
            scores_detail['logiciels'] = logiciels_score
            details.append(f"Logiciels: {len(matching_logiciels)}/{len(required_logiciels)} requis")
        else:
            scores_detail['logiciels'] = 85
            details.append("Logiciels: Aucune exigence")
        
        # Score global pondéré
        final_score = (
            scores_detail.get('techniques', 80) * 0.4 +
            scores_detail.get('langues', 85) * 0.3 +
            scores_detail.get('logiciels', 85) * 0.3
        )
        
        return {
            'competences': final_score,
            'competences_details': details,
            'competences_breakdown': scores_detail
        }
    
    def _apply_intelligent_reasoning(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any],
        candidat_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Applique le raisonnement intelligent pour identifier les correspondances spéciales
        """
        bonus_total = 0
        raisons = []
        recommandations = []
        
        # 1. ÉVOLUTION RAPIDE + PERSPECTIVES D'ÉVOLUTION
        if (candidat_profile['ambition'] == 'élevée' and 
            offre.get('perspectives_evolution', False)):
            bonus_total += self.config['bonus_intelligence']['evolution_rapide']
            raisons.append("Candidat ambitieux × Poste avec perspectives d'évolution")
            recommandations.append("Candidat idéal pour une promotion rapide")
        
        # 2. STABILITÉ + POSTE LONG TERME
        if (candidat_profile['stabilite'] == 'élevée' and 
            offre.get('duree_prevue', '').lower() in ['long terme', 'cdi', 'permanent']):
            bonus_total += self.config['bonus_intelligence']['stabilite']
            raisons.append("Candidat stable × Poste long terme")
            recommandations.append("Faible risque de turnover")
        
        # 3. INNOVATION + ENVIRONNEMENT CRÉATIF
        if (any('créatif' in pt or 'innovation' in pt for pt in candidat_profile['points_forts']) and
            ('innovation' in offre.get('culture_entreprise', {}).get('valeurs', []) or
             'créatif' in offre.get('environnement_travail', '').lower())):
            bonus_total += self.config['bonus_intelligence']['innovation']
            raisons.append("Profil créatif × Environnement innovant")
            recommandations.append("Excellente synergie créative attendue")
        
        # 4. LEADERSHIP + RESPONSABILITÉS
        if ('leadership' in candidat_profile['points_forts'] and
            ('management' in offre.get('responsabilites', '').lower() or
             'équipe' in offre.get('responsabilites', '').lower())):
            bonus_total += self.config['bonus_intelligence']['leadership']
            raisons.append("Potentiel de leadership × Responsabilités managériales")
            recommandations.append("Candidat prêt pour des responsabilités d'équipe")
        
        # 5. SPÉCIALISATION TECHNIQUE
        if (candidat_profile['niveau_experience'] == 'expert' and
            len(candidat_profile['specialisation']) > 0 and
            offre.get('niveau_technique', '').lower() in ['élevé', 'expert', 'senior']):
            bonus_total += self.config['bonus_intelligence']['specialisation']
            raisons.append("Expert technique × Poste à haute technicité")
            recommandations.append("Expertise technique parfaitement alignée")
        
        # 6. ADAPTABILITÉ + ENVIRONNEMENT CHANGEANT
        if ('polyvalent' in candidat_profile['points_forts'] and
            ('startup' in offre.get('type_entreprise', '').lower() or
             'agile' in offre.get('methodologie', '').lower())):
            bonus_total += self.config['bonus_intelligence']['adaptabilite']
            raisons.append("Profil polyvalent × Environnement agile")
            recommandations.append("Adaptation rapide aux changements")
        
        # 7. INTERNATIONAL + POSTE INTERNATIONAL
        if ('international' in candidat_profile['points_forts'] and
            (offre.get('dimension_internationale', False) or
             len(offre.get('langues_requises', [])) > 1)):
            bonus_total += 8
            raisons.append("Profil international × Poste multiculturel")
            recommandations.append("Atout pour le développement international")
        
        # 8. JUNIOR + FORMATION INTERNE
        if (candidat_profile['niveau_experience'] == 'junior' and
            offre.get('formation_interne', False)):
            bonus_total += 7
            raisons.append("Profil junior × Programme de formation")
            recommandations.append("Candidat avec fort potentiel de développement")
        
        return {
            'total': bonus_total,
            'raisons': raisons,
            'recommandations': recommandations
        }
    
    def _calculate_final_score(
        self, 
        scores: Dict[str, Any], 
        intelligence_bonus: Dict[str, Any]
    ) -> float:
        """
        Calcule le score final avec pondération et bonus intelligence
        """
        # Score de base pondéré
        base_score = (
            scores['localisation'] * self.config['ponderation']['localisation'] +
            scores['experience'] * self.config['ponderation']['experience'] +
            scores['remuneration'] * self.config['ponderation']['remuneration'] +
            scores['competences'] * self.config['ponderation']['competences']
        )
        
        # Ajouter le bonus intelligence
        final_score = base_score + intelligence_bonus['total']
        
        # Limiter entre 0 et 100
        return min(100, max(0, final_score))
    
    def _generate_intelligent_explanations(
        self,
        candidat: Dict[str, Any],
        offre: Dict[str, Any],
        scores: Dict[str, Any],
        intelligence_bonus: Dict[str, Any],
        candidat_profile: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Génère des explications intelligentes pour l'entreprise
        """
        explanations = {}
        
        # Résumé global
        total_score = self._calculate_final_score(scores, intelligence_bonus)
        
        if total_score >= 85:
            explanations['global'] = "🏆 CANDIDAT EXCELLENT - Correspondance exceptionnelle sur tous les critères"
        elif total_score >= 75:
            explanations['global'] = "✅ CANDIDAT RECOMMANDÉ - Très bonne correspondance générale"
        elif total_score >= 65:
            explanations['global'] = "⚖️ CANDIDAT VIABLE - Correspondance correcte avec quelques points d'attention"
        else:
            explanations['global'] = "⚠️ CANDIDAT À RISQUE - Correspondance faible, recrutement difficile"
        
        # Explication par critère
        if scores['localisation'] >= 80:
            explanations['localisation'] = "✅ Localisation excellente - Pas de problème de trajet"
        elif scores['localisation'] >= 60:
            explanations['localisation'] = "⚖️ Localisation acceptable - Trajet gérable"
        else:
            explanations['localisation'] = "⚠️ Localisation problématique - Trajet long ou difficile"
        
        if scores['experience'] >= 85:
            explanations['experience'] = "✅ Expérience parfaitement adaptée au poste"
        elif scores['experience'] >= 70:
            explanations['experience'] = "⚖️ Expérience convenable - Formation possible"
        else:
            explanations['experience'] = "⚠️ Expérience insuffisante - Risque d'échec"
        
        if scores['remuneration'] >= 80:
            explanations['remuneration'] = "✅ Prétentions salariales compatibles avec le budget"
        elif scores['remuneration'] >= 60:
            explanations['remuneration'] = "⚖️ Négociation salariale nécessaire"
        else:
            explanations['remuneration'] = "⚠️ Prétentions trop élevées - Recrutement coûteux"
        
        if scores['competences'] >= 85:
            explanations['competences'] = "✅ Compétences excellentes - Candidat opérationnel immédiatement"
        elif scores['competences'] >= 70:
            explanations['competences'] = "⚖️ Compétences correctes - Quelques formations à prévoir"
        else:
            explanations['competences'] = "⚠️ Compétences insuffisantes - Formation importante nécessaire"
        
        # Ajouter les insights intelligence
        if intelligence_bonus['raisons']:
            explanations['intelligence'] = "🧠 BONUS INTELLIGENCE: " + " | ".join(intelligence_bonus['raisons'])
        
        return explanations
    
    def _analyze_risks_opportunities(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Analyse les risques et opportunités du recrutement
        """
        risks = []
        opportunities = []
        
        # Analyse des risques
        experience = candidat.get('annees_experience', 0)
        required_exp = offre.get('experience_requise', 0)
        
        if experience > required_exp * 2:
            risks.append("Surqualification - Risque d'ennui et de départ rapide")
        
        if candidat.get('salaire_souhaite', 0) > offre.get('budget_max', 99999):
            risks.append("Prétentions salariales élevées - Risque de négociation difficile")
        
        if candidat.get('mobilite', '').lower() == 'limitée':
            risks.append("Mobilité limitée - Risque en cas de changement de lieu")
        
        duree_poste_actuel = candidat.get('duree_poste_actuel', 0)
        if duree_poste_actuel < 1:
            risks.append("Changements fréquents - Risque de faible rétention")
        
        # Analyse des opportunités
        if candidat.get('formation_continue', False):
            opportunities.append("Candidat en formation continue - Évolution compétences")
        
        if candidat.get('disponibilite', '').lower() == 'immédiate':
            opportunities.append("Disponibilité immédiate - Recrutement rapide possible")
        
        if 'international' in candidat.get('objectifs_carriere', {}).get('ambitions', []):
            opportunities.append("Ambitions internationales - Atout pour développement global")
        
        if candidat.get('niveau_etudes', '').lower() in ['master', 'ingénieur', 'doctorat']:
            opportunities.append("Niveau d'études élevé - Potentiel d'évolution important")
        
        return {
            'risques': risks,
            'opportunites': opportunities
        }
    
    # Méthodes utilitaires
    
    def _same_region(self, location1: str, location2: str) -> bool:
        """Vérifie si deux localisations sont dans la même région"""
        # Simplification - peut être améliorée avec une vraie API géographique
        common_regions = [
            ['paris', 'ile-de-france', 'idf', '75', '92', '93', '94', '95'],
            ['lyon', 'rhône-alpes', 'auvergne-rhône-alpes', '69'],
            ['marseille', 'paca', "provence-alpes-côte d'azur", '13'],
            ['toulouse', 'occitanie', 'midi-pyrénées', '31'],
            ['bordeaux', 'nouvelle-aquitaine', 'gironde', '33']
        ]
        
        for region in common_regions:
            if any(term in location1 for term in region) and any(term in location2 for term in region):
                return True
        
        return False
    
    def _estimate_distance(self, location1: str, location2: str) -> int:
        """Estime la distance en km entre deux villes (simplifiée)"""
        # Distances approximatives entre grandes villes françaises
        distances = {
            ('paris', 'lyon'): 470,
            ('paris', 'marseille'): 780,
            ('paris', 'toulouse'): 680,
            ('paris', 'bordeaux'): 580,
            ('lyon', 'marseille'): 320,
            ('lyon', 'toulouse'): 540,
            ('marseille', 'toulouse'): 420,
            # etc.
        }
        
        # Simplification pour l'exemple
        for (city1, city2), distance in distances.items():
            if (city1 in location1 and city2 in location2) or (city2 in location1 and city1 in location2):
                return distance
        
        # Distance par défaut
        return 50
    
    def _parse_salary_range(self, salary_str: str, budget_max: int = 0) -> Tuple[int, int]:
        """Parse la fourchette salariale"""
        if budget_max > 0:
            return (int(budget_max * 0.8), budget_max)
        
        if not salary_str:
            return None
        
        # Recherche de patterns comme "40-50K€" ou "45000-55000€"
        import re
        
        # Pattern pour "40-50K"
        pattern_k = r'(\d+)-(\d+)k'
        match_k = re.search(pattern_k, salary_str.lower())
        if match_k:
            return (int(match_k.group(1)) * 1000, int(match_k.group(2)) * 1000)
        
        # Pattern pour "40000-50000"
        pattern_full = r'(\d+)-(\d+)'
        match_full = re.search(pattern_full, salary_str)
        if match_full:
            return (int(match_full.group(1)), int(match_full.group(2)))
        
        # Pattern pour un seul nombre "45K"
        pattern_single = r'(\d+)k'
        match_single = re.search(pattern_single, salary_str.lower())
        if match_single:
            base = int(match_single.group(1)) * 1000
            return (int(base * 0.9), int(base * 1.1))
        
        return None
    
    def _create_fallback_result(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any], 
        index: int
    ) -> Dict[str, Any]:
        """Crée un résultat de fallback en cas d'erreur"""
        return {
            'id': offre.get('id', f'job_{index}'),
            'titre': offre.get('titre', 'Poste sans titre'),
            'entreprise': offre.get('entreprise', 'Entreprise'),
            'matching_score_entreprise': 60,
            'scores_detailles': {
                'localisation': {'pourcentage': 60, 'details': ['Analyse limitée']},
                'experience': {'pourcentage': 60, 'details': ['Analyse limitée']},
                'remuneration': {'pourcentage': 60, 'details': ['Analyse limitée']},
                'competences': {'pourcentage': 60, 'details': ['Analyse limitée']}
            },
            'intelligence': {
                'bonus_applique': 0,
                'raisons': [],
                'recommandations': ['Analyse détaillée recommandée']
            },
            'explications_entreprise': {
                'global': 'Analyse simplifiée - Données insuffisantes'
            },
            'analyse_risques': {
                'risques': ['Données insuffisantes pour analyse complète'],
                'opportunites': []
            },
            'profil_candidat': {'type_profil': 'standard'},
            **offre
        }
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'algorithme SuperSmartMatch"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": {
                "intelligent_reasoning": True,
                "company_perspective": True,
                "detailed_scoring": True,
                "location_analysis": True,
                "salary_compatibility": True,
                "skills_breakdown": True,
                "risk_analysis": True,
                "evolution_matching": True
            },
            "scoring_criteria": {
                "localisation": "Temps de trajet, mobilité, télétravail",
                "experience": "Adéquation niveau, potentiel, surqualification",
                "remuneration": "Compatibilité budget entreprise",
                "competences": "Techniques, langues, logiciels"
            },
            "intelligent_bonuses": [
                "Évolution rapide × Perspectives",
                "Stabilité × Poste long terme", 
                "Innovation × Environnement créatif",
                "Leadership × Responsabilités",
                "Spécialisation × Technicité",
                "Adaptabilité × Agilité"
            ],
            "initialized": self.initialized
        }
