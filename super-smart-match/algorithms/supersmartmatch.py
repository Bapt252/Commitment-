#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch Algorithm v2.1 - Algorithme intelligent avec pondération dynamique
Calcule des pourcentages de correspondance précis sur :
- Proximité (localisation, temps de trajet)
- Expérience
- Rémunération
- Flexibilité (télétravail, horaires flexibles, RTT) ⭐ NOUVEAU
- Raisonnement intelligent (évolution rapide, perspectives, etc.)

⚡ NOUVEAUTÉ v2.1: Pondération dynamique basée sur 4 leviers candidat
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
    Algorithme SuperSmartMatch v2.1 avec pondération dynamique intelligente
    """
    
    def __init__(self):
        super().__init__()
        self.name = "supersmartmatch"
        self.description = "Algorithme intelligent avec pondération dynamique et scoring flexibilité"
        self.version = "2.1"
        self.initialized = True
        
        # Configuration des seuils intelligents
        self.config = {
            'seuils': {
                'proximite': {  # Renommé de 'localisation'
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
                },
                'flexibilite': {  # ⭐ NOUVEAU CRITÈRE
                    'parfait': 95,     # Toutes exigences flexibilité respectées
                    'excellent': 85,   # Majorité des exigences
                    'bon': 70,         # Quelques exigences
                    'limite': 50       # Flexibilité limitée
                }
            },
            # ⚡ PONDÉRATION DYNAMIQUE (remplace la pondération fixe)
            'ponderation_base': {
                'proximite': 0.25,    # Renommé de 'localisation'
                'experience': 0.20,   # Réduit pour faire place à 'flexibilite'
                'remuneration': 0.25,
                'competences': 0.15,  # Réduit pour faire place à 'flexibilite'
                'flexibilite': 0.15   # ⭐ NOUVEAU
            },
            # 🎛️ CORRESPONDANCE LEVIERS CANDIDAT → CRITÈRES ALGORITHM
            'leviers_mapping': {
                'evolution': ['experience', 'competences'],  # Évolution → Expérience + Compétences
                'remuneration': ['remuneration'],            # Rémunération → Rémunération
                'proximite': ['proximite'],                  # Proximité → Proximité
                'flexibilite': ['flexibilite']               # Flexibilité → Flexibilité
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
        Exécute le matching SuperSmartMatch v2.1 avec pondération dynamique
        
        Args:
            candidat: Données du candidat (avec questionnaire_data optionnel)
            offres: Liste des offres d'emploi
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des offres avec scores de matching dynamiques
        """
        logger.info(f"🚀 Démarrage SuperSmartMatch v2.1 pour {len(offres)} offres")
        
        # ⚡ CALCUL PONDÉRATION DYNAMIQUE
        dynamic_weights = self.calculate_dynamic_weights(candidat)
        logger.info(f"🎛️ Pondération dynamique: {dynamic_weights}")
        
        results = []
        candidat_profile = self._analyze_candidate_profile(candidat)
        
        for i, offre in enumerate(offres[:limit]):
            try:
                # Calcul des scores détaillés (avec nouveau critère flexibilité)
                scores = self._calculate_detailed_scores(candidat, offre, candidat_profile)
                
                # Application du raisonnement intelligent
                intelligence_bonus = self._apply_intelligent_reasoning(candidat, offre, candidat_profile)
                
                # ⚡ Score final avec pondération DYNAMIQUE
                final_score = self._calculate_final_score_dynamic(scores, intelligence_bonus, dynamic_weights)
                
                # Génération des explications intelligentes
                explanations = self._generate_intelligent_explanations(
                    candidat, offre, scores, intelligence_bonus, candidat_profile, dynamic_weights
                )
                
                result = {
                    'id': offre.get('id', f'job_{i}'),
                    'titre': offre.get('titre', offre.get('title', 'Poste sans titre')),
                    'entreprise': offre.get('entreprise', 'Entreprise non spécifiée'),
                    
                    # Score principal avec pondération dynamique
                    'matching_score_entreprise': int(final_score),
                    
                    # ⚡ NOUVEAUTÉ: Pondération utilisée pour ce candidat
                    'ponderation_dynamique': dynamic_weights,
                    
                    # Détails des scores par critère (incluant flexibilité)
                    'scores_detailles': {
                        'proximite': {
                            'pourcentage': int(scores['proximite']),
                            'details': scores['proximite_details'],
                            'poids': round(dynamic_weights['proximite'] * 100, 1)
                        },
                        'experience': {
                            'pourcentage': int(scores['experience']),
                            'details': scores['experience_details'],
                            'poids': round(dynamic_weights['experience'] * 100, 1)
                        },
                        'remuneration': {
                            'pourcentage': int(scores['remuneration']),
                            'details': scores['remuneration_details'],
                            'poids': round(dynamic_weights['remuneration'] * 100, 1)
                        },
                        'competences': {
                            'pourcentage': int(scores['competences']),
                            'details': scores['competences_details'],
                            'poids': round(dynamic_weights['competences'] * 100, 1)
                        },
                        'flexibilite': {  # ⭐ NOUVEAU
                            'pourcentage': int(scores['flexibilite']),
                            'details': scores['flexibilite_details'],
                            'poids': round(dynamic_weights['flexibilite'] * 100, 1)
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
                result = self._create_fallback_result(candidat, offre, i, dynamic_weights)
                results.append(result)
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['matching_score_entreprise'], reverse=True)
        
        logger.info(f"✅ SuperSmartMatch v2.1 terminé - {len(results)} résultats générés")
        return results
    
    def calculate_dynamic_weights(self, candidat: Dict[str, Any]) -> Dict[str, float]:
        """
        🎛️ FONCTION CENTRALE: Calcule la pondération dynamique basée sur les priorités candidat
        
        Args:
            candidat: Données candidat avec questionnaire_data optionnel
            
        Returns:
            Dict avec pondération adaptée aux priorités du candidat
        """
        # Récupérer les priorités candidat du questionnaire
        questionnaire = candidat.get('questionnaire_data', {})
        priorites = questionnaire.get('priorites_candidat', {})
        
        logger.info(f"📋 Priorités candidat trouvées: {priorites}")
        
        # Si pas de priorités, utiliser pondération de base
        if not priorites:
            logger.info("🔄 Aucune priorité définie - Utilisation pondération de base")
            return self.config['ponderation_base'].copy()
        
        # Normaliser les notes (au cas où elles ne seraient pas sur 10)
        notes_normalisees = {}
        for levier, note in priorites.items():
            if isinstance(note, (int, float)) and note > 0:
                # Assurer que la note est entre 1 et 10
                notes_normalisees[levier] = max(1, min(10, float(note)))
        
        if not notes_normalisees:
            logger.warning("⚠️ Notes priorités invalides - Utilisation pondération de base")
            return self.config['ponderation_base'].copy()
        
        logger.info(f"✅ Notes normalisées: {notes_normalisees}")
        
        # Calculer les poids dynamiques
        # Plus la note est élevée, plus le poids augmente
        total_notes = sum(notes_normalisees.values())
        
        # Calculer le facteur de distribution pour chaque levier
        facteurs_leviers = {}
        for levier, note in notes_normalisees.items():
            # Facteur entre 0.5 et 2.0 basé sur la note
            # Note 10 = facteur 2.0, Note 5 = facteur 1.0, Note 1 = facteur 0.5
            facteurs_leviers[levier] = 0.5 + (note - 1) * (1.5 / 9)
        
        logger.info(f"📊 Facteurs par levier: {facteurs_leviers}")
        
        # Appliquer les facteurs aux critères correspondants
        weights_ajustes = {}
        
        for critere, poids_base in self.config['ponderation_base'].items():
            facteur_total = 1.0
            nb_leviers = 0
            
            # Trouver quels leviers influencent ce critère
            for levier, criteres_lies in self.config['leviers_mapping'].items():
                if critere in criteres_lies and levier in facteurs_leviers:
                    facteur_total *= facteurs_leviers[levier]
                    nb_leviers += 1
            
            # Si plusieurs leviers influencent le critère, prendre la moyenne géométrique
            if nb_leviers > 1:
                facteur_total = facteur_total ** (1/nb_leviers)
            
            weights_ajustes[critere] = poids_base * facteur_total
        
        # Normaliser pour que la somme = 1.0
        total_poids = sum(weights_ajustes.values())
        weights_normalises = {
            critere: poids / total_poids 
            for critere, poids in weights_ajustes.items()
        }
        
        logger.info(f"🎯 Pondération dynamique finale: {weights_normalises}")
        
        # Calculer les variations par rapport à la base
        variations = {}
        for critere in weights_normalises:
            variation = ((weights_normalises[critere] / self.config['ponderation_base'][critere]) - 1) * 100
            variations[critere] = round(variation, 1)
        
        logger.info(f"📈 Variations vs base: {variations}")
        
        return weights_normalises
    
    def _calculate_detailed_scores(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any],
        candidat_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule les scores détaillés pour chaque critère (avec nouveau critère flexibilité)
        """
        scores = {}
        
        # 1. PROXIMITÉ (anciennement localisation)
        scores.update(self._calculate_location_score_detailed(candidat, offre))
        
        # 2. EXPÉRIENCE
        scores.update(self._calculate_experience_score_detailed(candidat, offre, candidat_profile))
        
        # 3. RÉMUNÉRATION
        scores.update(self._calculate_salary_score_detailed(candidat, offre))
        
        # 4. COMPÉTENCES
        scores.update(self._calculate_skills_score_detailed(candidat, offre))
        
        # 5. ⭐ FLEXIBILITÉ (NOUVEAU)
        scores.update(self._calculate_flexibility_score_detailed(candidat, offre))
        
        return scores
    
    def _calculate_flexibility_score_detailed(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ⭐ NOUVEAU: Calcule le score de flexibilité (télétravail, horaires, RTT)
        """
        score = 70  # Score de base
        details = []
        
        # Récupérer les préférences flexibilité candidat
        questionnaire = candidat.get('questionnaire_data', {})
        flex_candidat = questionnaire.get('flexibilite_attendue', {})
        
        # Préférences générales du candidat
        candidat_remote = candidat.get('preferences_remote', '')
        candidat_horaires = candidat.get('horaires_flexibles', False)
        
        # Politique de l'entreprise
        offre_remote = offre.get('politique_remote', '').lower()
        offre_horaires = offre.get('horaires_flexibles', False)
        offre_rtt = offre.get('jours_rtt', 0)
        offre_avantages = offre.get('avantages', [])
        
        score_components = []
        
        # 1. TÉLÉTRAVAIL (40% du score flexibilité)
        if flex_candidat.get('teletravail') or 'télétravail' in str(candidat_remote).lower():
            candidat_want_remote = True
            if flex_candidat.get('teletravail') == 'total':
                remote_preference = 'total'
            elif flex_candidat.get('teletravail') == 'partiel':
                remote_preference = 'partiel'
            else:
                remote_preference = 'ouvert'
        else:
            candidat_want_remote = False
            remote_preference = 'aucun'
        
        if candidat_want_remote:
            if 'télétravail' in offre_remote or 'remote' in offre_remote:
                if 'total' in offre_remote and remote_preference == 'total':
                    score_teletravail = 100
                    details.append("✅ Télétravail total possible - Parfait match")
                elif 'partiel' in offre_remote:
                    score_teletravail = 85 if remote_preference != 'total' else 75
                    details.append("✅ Télétravail partiel possible - Bon compromis")
                else:
                    score_teletravail = 80
                    details.append("✅ Télétravail disponible")
            else:
                score_teletravail = 30
                details.append("❌ Pas de télétravail possible - Attente non satisfaite")
        else:
            if 'télétravail' in offre_remote:
                score_teletravail = 85
                details.append("⚖️ Télétravail disponible mais non souhaité")
            else:
                score_teletravail = 90
                details.append("✅ Travail en présentiel - Correspondance parfaite")
        
        score_components.append(('teletravail', score_teletravail, 0.4))
        
        # 2. HORAIRES FLEXIBLES (35% du score flexibilité)
        candidat_want_flex = (flex_candidat.get('horaires_flexibles', False) or 
                             candidat_horaires or 
                             'flexible' in str(candidat.get('contraintes_horaires', '')).lower())
        
        if candidat_want_flex:
            if offre_horaires or 'flexible' in ' '.join(offre_avantages).lower():
                score_horaires = 95
                details.append("✅ Horaires flexibles disponibles - Excellent")
            else:
                score_horaires = 45
                details.append("❌ Horaires fixes - Flexibilité non disponible")
        else:
            score_horaires = 80
            details.append("⚖️ Horaires: Pas d'exigence particulière")
        
        score_components.append(('horaires', score_horaires, 0.35))
        
        # 3. RTT et CONGÉS (25% du score flexibilité)
        candidat_rtt_important = flex_candidat.get('rtt_important', False)
        
        if candidat_rtt_important:
            if offre_rtt >= 15:  # Plus de 15 RTT = excellent
                score_rtt = 95
                details.append(f"✅ {offre_rtt} jours RTT - Excellent équilibre")
            elif offre_rtt >= 10:  # 10-15 RTT = bon
                score_rtt = 80
                details.append(f"✅ {offre_rtt} jours RTT - Bon équilibre")
            elif offre_rtt >= 5:   # 5-10 RTT = acceptable
                score_rtt = 65
                details.append(f"⚖️ {offre_rtt} jours RTT - Équilibre moyen")
            else:  # Moins de 5 RTT = insuffisant
                score_rtt = 40
                details.append(f"❌ Seulement {offre_rtt} jours RTT - Insuffisant")
        else:
            score_rtt = 75
            details.append("⚖️ RTT: Pas d'exigence particulière")
        
        score_components.append(('rtt', score_rtt, 0.25))
        
        # Calcul du score final pondéré
        final_score = sum(score * weight for _, score, weight in score_components)
        
        # Ajouter détails de calcul
        calcul_details = [f"{name}: {score}% (poids {weight*100}%)" 
                         for name, score, weight in score_components]
        details.extend(calcul_details)
        
        logger.info(f"🔄 Score flexibilité: {final_score:.1f}% - {details}")
        
        return {
            'flexibilite': final_score,
            'flexibilite_details': details
        }
    
    def _calculate_final_score_dynamic(
        self, 
        scores: Dict[str, Any], 
        intelligence_bonus: Dict[str, Any],
        dynamic_weights: Dict[str, float]
    ) -> float:
        """
        ⚡ NOUVEAU: Calcule le score final avec pondération DYNAMIQUE
        """
        # Score de base pondéré dynamiquement
        base_score = (
            scores['proximite'] * dynamic_weights['proximite'] +
            scores['experience'] * dynamic_weights['experience'] +
            scores['remuneration'] * dynamic_weights['remuneration'] +
            scores['competences'] * dynamic_weights['competences'] +
            scores['flexibilite'] * dynamic_weights['flexibilite']  # ⭐ NOUVEAU
        )
        
        # Ajouter le bonus intelligence
        final_score = base_score + intelligence_bonus['total']
        
        # Limiter entre 0 et 100
        return min(100, max(0, final_score))
    
    def _calculate_location_score_detailed(
        self, 
        candidat: Dict[str, Any], 
        offre: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcule le score de proximité (renommé de localisation)
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
            'proximite': score,  # Renommé de 'localisation'
            'proximite_details': details
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
    
    def _generate_intelligent_explanations(
        self,
        candidat: Dict[str, Any],
        offre: Dict[str, Any],
        scores: Dict[str, Any],
        intelligence_bonus: Dict[str, Any],
        candidat_profile: Dict[str, Any],
        dynamic_weights: Dict[str, float]
    ) -> Dict[str, str]:
        """
        Génère des explications intelligentes avec info sur pondération dynamique
        """
        explanations = {}
        
        # Résumé global
        total_score = self._calculate_final_score_dynamic(scores, intelligence_bonus, dynamic_weights)
        
        if total_score >= 85:
            explanations['global'] = "🏆 CANDIDAT EXCELLENT - Correspondance exceptionnelle sur tous les critères"
        elif total_score >= 75:
            explanations['global'] = "✅ CANDIDAT RECOMMANDÉ - Très bonne correspondance générale"
        elif total_score >= 65:
            explanations['global'] = "⚖️ CANDIDAT VIABLE - Correspondance correcte avec quelques points d'attention"
        else:
            explanations['global'] = "⚠️ CANDIDAT À RISQUE - Correspondance faible, recrutement difficile"
        
        # ⚡ Explication pondération dynamique
        priorites_info = []
        for critere, poids in dynamic_weights.items():
            poids_base = self.config['ponderation_base'][critere]
            if poids > poids_base * 1.1:
                priorites_info.append(f"{critere.upper()}: priorité élevée ({poids*100:.1f}%)")
            elif poids < poids_base * 0.9:
                priorites_info.append(f"{critere}: priorité réduite ({poids*100:.1f}%)")
        
        if priorites_info:
            explanations['ponderation'] = "🎛️ PONDÉRATION ADAPTÉE: " + " | ".join(priorites_info)
        
        # Explication par critère
        if scores['proximite'] >= 80:
            explanations['proximite'] = "✅ Proximité excellente - Pas de problème de trajet"
        elif scores['proximite'] >= 60:
            explanations['proximite'] = "⚖️ Proximité acceptable - Trajet gérable"
        else:
            explanations['proximite'] = "⚠️ Proximité problématique - Trajet long ou difficile"
        
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
        
        # ⭐ NOUVEAU: Explication flexibilité
        if scores['flexibilite'] >= 85:
            explanations['flexibilite'] = "✅ Flexibilité excellente - Attentes parfaitement satisfaites"
        elif scores['flexibilite'] >= 70:
            explanations['flexibilite'] = "⚖️ Flexibilité correcte - Quelques compromis nécessaires"
        else:
            explanations['flexibilite'] = "⚠️ Flexibilité insuffisante - Attentes non satisfaites"
        
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
    
    # Méthodes utilitaires (maintenues identiques)
    
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
        index: int,
        dynamic_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Crée un résultat de fallback en cas d'erreur"""
        return {
            'id': offre.get('id', f'job_{index}'),
            'titre': offre.get('titre', 'Poste sans titre'),
            'entreprise': offre.get('entreprise', 'Entreprise'),
            'matching_score_entreprise': 60,
            'ponderation_dynamique': dynamic_weights,
            'scores_detailles': {
                'proximite': {'pourcentage': 60, 'details': ['Analyse limitée'], 'poids': round(dynamic_weights.get('proximite', 0.25)*100, 1)},
                'experience': {'pourcentage': 60, 'details': ['Analyse limitée'], 'poids': round(dynamic_weights.get('experience', 0.25)*100, 1)},
                'remuneration': {'pourcentage': 60, 'details': ['Analyse limitée'], 'poids': round(dynamic_weights.get('remuneration', 0.25)*100, 1)},
                'competences': {'pourcentage': 60, 'details': ['Analyse limitée'], 'poids': round(dynamic_weights.get('competences', 0.25)*100, 1)},
                'flexibilite': {'pourcentage': 60, 'details': ['Analyse limitée'], 'poids': round(dynamic_weights.get('flexibilite', 0.15)*100, 1)}
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
        """Retourne les informations sur l'algorithme SuperSmartMatch v2.1"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "new_features": {
                "dynamic_weighting": "Pondération adaptée aux priorités candidat",
                "flexibility_scoring": "Nouveau critère flexibilité (télétravail, horaires, RTT)",
                "candidate_priorities": "Support questionnaire_data avec notes 1-10",
                "bidirectional_matching": "Matching personnalisé dans les deux sens"
            },
            "capabilities": {
                "intelligent_reasoning": True,
                "company_perspective": True,
                "detailed_scoring": True,
                "location_analysis": True,
                "salary_compatibility": True,
                "skills_breakdown": True,
                "flexibility_analysis": True,  # ⭐ NOUVEAU
                "dynamic_weighting": True,    # ⭐ NOUVEAU
                "risk_analysis": True,
                "evolution_matching": True
            },
            "scoring_criteria": {
                "proximite": "Temps de trajet, mobilité, télétravail",
                "experience": "Adéquation niveau, potentiel, surqualification",
                "remuneration": "Compatibilité budget entreprise",
                "competences": "Techniques, langues, logiciels",
                "flexibilite": "Télétravail, horaires flexibles, RTT"  # ⭐ NOUVEAU
            },
            "dynamic_levers": {  # ⭐ NOUVEAU
                "evolution": "Perspectives, ambition, formation → Influence expérience + compétences",
                "remuneration": "Salaire, avantages → Influence rémunération",
                "proximite": "Localisation, temps trajet → Influence proximité",
                "flexibilite": "Télétravail, horaires, RTT → Influence flexibilité"
            },
            "questionnaire_structure": {  # ⭐ NOUVEAU
                "priorites_candidat": {
                    "evolution": "Note 1-10",
                    "remuneration": "Note 1-10",
                    "proximite": "Note 1-10",
                    "flexibilite": "Note 1-10"
                },
                "flexibilite_attendue": {
                    "teletravail": "aucun/partiel/total",
                    "horaires_flexibles": "boolean",
                    "rtt_important": "boolean"
                }
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

# ===== 🧪 TESTS INTÉGRÉS =====

def test_dynamic_weighting():
    """
    🧪 Tests pour valider la pondération dynamique
    """
    print("🧪 === TESTS PONDÉRATION DYNAMIQUE ===")
    
    algorithm = SuperSmartMatchAlgorithm()
    
    # Test 1: Candidat "salaire prioritaire"
    print("\n📊 Test 1: Candidat salaire prioritaire")
    candidat_salaire = {
        'id': 'test_1',
        'annees_experience': 5,
        'salaire_souhaite': 50000,
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 3,      # Faible
                'remuneration': 9,   # Très élevé
                'proximite': 6,      # Moyen
                'flexibilite': 5     # Moyen
            }
        }
    }
    
    weights_salaire = algorithm.calculate_dynamic_weights(candidat_salaire)
    print(f"Pondération adaptée: {weights_salaire}")
    assert weights_salaire['remuneration'] > algorithm.config['ponderation_base']['remuneration']
    print("✅ Test 1 réussi: Rémunération bien priorisée")
    
    # Test 2: Candidat "évolution prioritaire"
    print("\n📊 Test 2: Candidat évolution prioritaire")
    candidat_evolution = {
        'id': 'test_2',
        'annees_experience': 3,
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 10,     # Maximum
                'remuneration': 4,   # Faible
                'proximite': 5,      # Moyen
                'flexibilite': 6     # Moyen
            }
        }
    }
    
    weights_evolution = algorithm.calculate_dynamic_weights(candidat_evolution)
    print(f"Pondération adaptée: {weights_evolution}")
    # Évolution influence experience + competences
    assert (weights_evolution['experience'] > algorithm.config['ponderation_base']['experience'] or
            weights_evolution['competences'] > algorithm.config['ponderation_base']['competences'])
    print("✅ Test 2 réussi: Évolution bien priorisée")
    
    # Test 3: Candidat "flexibilité prioritaire"
    print("\n📊 Test 3: Candidat flexibilité prioritaire")
    candidat_flex = {
        'id': 'test_3',
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 4,      # Faible
                'remuneration': 5,   # Moyen
                'proximite': 3,      # Faible
                'flexibilite': 10    # Maximum
            },
            'flexibilite_attendue': {
                'teletravail': 'partiel',
                'horaires_flexibles': True,
                'rtt_important': True
            }
        }
    }
    
    weights_flex = algorithm.calculate_dynamic_weights(candidat_flex)
    print(f"Pondération adaptée: {weights_flex}")
    assert weights_flex['flexibilite'] > algorithm.config['ponderation_base']['flexibilite']
    print("✅ Test 3 réussi: Flexibilité bien priorisée")
    
    # Test 4: Pas de questionnaire (fallback)
    print("\n📊 Test 4: Pas de questionnaire (fallback)")
    candidat_vide = {'id': 'test_4'}
    weights_vide = algorithm.calculate_dynamic_weights(candidat_vide)
    assert weights_vide == algorithm.config['ponderation_base']
    print("✅ Test 4 réussi: Fallback vers pondération de base")
    
    print("\n🎉 Tous les tests de pondération dynamique réussis!")

def test_flexibility_scoring():
    """
    🧪 Tests pour valider le scoring flexibilité
    """
    print("\n🧪 === TESTS SCORING FLEXIBILITÉ ===")
    
    algorithm = SuperSmartMatchAlgorithm()
    
    # Test offre avec télétravail partiel + horaires flexibles
    offre_flexible = {
        'id': 'job_flex',
        'titre': 'Développeur Full Stack',
        'politique_remote': 'télétravail partiel possible',
        'horaires_flexibles': True,
        'jours_rtt': 12,
        'avantages': ['mutuelle', 'tickets resto']
    }
    
    # Test candidat qui veut télétravail + flexibilité
    candidat_flexible = {
        'questionnaire_data': {
            'flexibilite_attendue': {
                'teletravail': 'partiel',
                'horaires_flexibles': True,
                'rtt_important': True
            }
        }
    }
    
    scores = algorithm._calculate_flexibility_score_detailed(candidat_flexible, offre_flexible)
    print(f"Score flexibilité: {scores['flexibilite']:.1f}%")
    print(f"Détails: {scores['flexibilite_details']}")
    
    assert scores['flexibilite'] >= 80  # Devrait être élevé
    print("✅ Test flexibilité réussi: Score élevé pour correspondance")
    
    print("\n🎉 Tests scoring flexibilité réussis!")

if __name__ == "__main__":
    # Exécuter les tests si le script est lancé directement
    test_dynamic_weighting()
    test_flexibility_scoring()
    print("\n🚀 SuperSmartMatch v2.1 avec pondération dynamique prêt!")
