#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sélecteur Intelligent d'Algorithmes pour SuperSmartMatch

Analyse le contexte et sélectionne automatiquement le meilleur algorithme :
- Analyse du profil candidat
- Analyse du volume de données
- Contraintes de performance
- Préférences utilisateur

Auteur: Nexten Team
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class AlgorithmSelector:
    """
    Sélecteur intelligent d'algorithme basé sur le contexte
    """
    
    def __init__(self):
        # Règles de sélection d'algorithme
        self.selection_rules = {
            # Règles basées sur le volume de données
            'volume_rules': {
                'small': {'max_jobs': 50, 'recommended': ['enhanced', 'semantic', 'smart-match']},
                'medium': {'max_jobs': 200, 'recommended': ['enhanced', 'hybrid', 'smart-match']},
                'large': {'max_jobs': 1000, 'recommended': ['original', 'enhanced', 'hybrid']},
                'very_large': {'max_jobs': float('inf'), 'recommended': ['original', 'hybrid']}
            },
            
            # Règles basées sur l'expérience candidat
            'experience_rules': {
                'junior': {'max_years': 2, 'recommended': ['smart-match', 'enhanced']},
                'mid': {'max_years': 5, 'recommended': ['enhanced', 'hybrid', 'semantic']},
                'senior': {'max_years': 10, 'recommended': ['enhanced', 'semantic', 'hybrid']},
                'expert': {'max_years': float('inf'), 'recommended': ['semantic', 'hybrid', 'enhanced']}
            },
            
            # Règles basées sur les compétences
            'skills_rules': {
                'technical': {
                    'keywords': ['python', 'javascript', 'java', 'react', 'django', 'sql', 'aws'],
                    'recommended': ['semantic', 'enhanced', 'hybrid']
                },
                'management': {
                    'keywords': ['management', 'équipe', 'chef', 'directeur', 'responsable'],
                    'recommended': ['smart-match', 'enhanced']
                },
                'creative': {
                    'keywords': ['design', 'créatif', 'marketing', 'communication'],
                    'recommended': ['enhanced', 'smart-match']
                }
            },
            
            # Règles basées sur la géolocalisation
            'location_rules': {
                'mobile': {
                    'keywords': ['remote', 'télétravail', 'national', 'france'],
                    'recommended': ['smart-match', 'enhanced']
                },
                'local': {
                    'keywords': ['paris', 'lyon', 'marseille', 'toulouse'],
                    'recommended': ['smart-match', 'enhanced', 'hybrid']
                }
            }
        }
        
        # Métriques de performance par algorithme (à ajuster selon les benchmarks)
        self.performance_profiles = {
            'original': {
                'speed': 10,
                'accuracy': 6,
                'memory': 9,
                'best_volume': 'large'
            },
            'enhanced': {
                'speed': 7,
                'accuracy': 9,
                'memory': 7,
                'best_volume': 'medium'
            },
            'semantic': {
                'speed': 6,
                'accuracy': 8,
                'memory': 6,
                'best_volume': 'small'
            },
            'smart-match': {
                'speed': 8,
                'accuracy': 8,
                'memory': 8,
                'best_volume': 'medium'
            },
            'hybrid': {
                'speed': 5,
                'accuracy': 10,
                'memory': 5,
                'best_volume': 'medium'
            },
            'custom': {
                'speed': 8,
                'accuracy': 7,
                'memory': 8,
                'best_volume': 'medium'
            }
        }
    
    def recommend_algorithm(self, candidate_data: Dict[str, Any], jobs_count: int, 
                          options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Recommande le meilleur algorithme basé sur le contexte
        
        Args:
            candidate_data: Données du candidat
            jobs_count: Nombre d'offres à analyser
            options: Options supplémentaires (performance_priority, accuracy_priority, etc.)
        
        Returns:
            Dict avec l'algorithme recommandé et les raisons
        """
        if options is None:
            options = {}
        
        logger.info(f"Sélection d'algorithme - Candidat exp: {candidate_data.get('annees_experience', 0)}, Jobs: {jobs_count}")
        
        # Analyse du contexte
        context = self._analyze_context(candidate_data, jobs_count, options)
        
        # Calcul des scores pour chaque algorithme
        algorithm_scores = self._calculate_algorithm_scores(context)
        
        # Sélection du meilleur algorithme
        best_algorithm = max(algorithm_scores.items(), key=lambda x: x[1]['total_score'])
        
        # Préparation de la réponse
        recommendation = {
            'algorithm': best_algorithm[0],
            'confidence': min(100, round(best_algorithm[1]['total_score'])),
            'reasoning': self._generate_reasoning(context, best_algorithm[0], algorithm_scores),
            'alternatives': self._get_alternatives(algorithm_scores, best_algorithm[0]),
            'performance_prediction': self._predict_performance(best_algorithm[0], context),
            'context_analysis': context
        }
        
        logger.info(f"Algorithme sélectionné: {recommendation['algorithm']} (confiance: {recommendation['confidence']}%)")
        
        return recommendation
    
    def _analyze_context(self, candidate_data: Dict[str, Any], jobs_count: int, 
                        options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse le contexte pour la sélection d'algorithme
        """
        context = {
            'candidate_experience': candidate_data.get('annees_experience', 0),
            'candidate_skills': candidate_data.get('competences', []),
            'candidate_location': candidate_data.get('adresse', ''),
            'jobs_count': jobs_count,
            'performance_priority': options.get('performance_priority', 'balanced'),
            'accuracy_priority': options.get('accuracy_priority', 'high'),
            'time_constraint': options.get('max_processing_time', None)
        }
        
        # Classification du volume
        context['volume_category'] = self._classify_volume(jobs_count)
        
        # Classification de l'expérience
        context['experience_category'] = self._classify_experience(context['candidate_experience'])
        
        # Classification des compétences
        context['skills_category'] = self._classify_skills(context['candidate_skills'])
        
        # Classification de la mobilité
        context['mobility_category'] = self._classify_mobility(candidate_data)
        
        return context
    
    def _classify_volume(self, jobs_count: int) -> str:
        """Classifie le volume de données"""
        if jobs_count <= 50:
            return 'small'
        elif jobs_count <= 200:
            return 'medium'
        elif jobs_count <= 1000:
            return 'large'
        else:
            return 'very_large'
    
    def _classify_experience(self, experience_years: int) -> str:
        """Classifie le niveau d'expérience"""
        if experience_years <= 2:
            return 'junior'
        elif experience_years <= 5:
            return 'mid'
        elif experience_years <= 10:
            return 'senior'
        else:
            return 'expert'
    
    def _classify_skills(self, skills: List[str]) -> str:
        """Classifie le type de compétences"""
        skills_text = ' '.join(skills).lower()
        
        # Compter les correspondances par catégorie
        categories_scores = {}
        for category, rule in self.selection_rules['skills_rules'].items():
            score = sum(1 for keyword in rule['keywords'] if keyword.lower() in skills_text)
            categories_scores[category] = score
        
        # Retourner la catégorie avec le plus de correspondances
        if categories_scores:
            best_category = max(categories_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                return best_category[0]
        
        return 'general'  # Catégorie par défaut
    
    def _classify_mobility(self, candidate_data: Dict[str, Any]) -> str:
        """Classifie la mobilité du candidat"""
        location = candidate_data.get('adresse', '').lower()
        mobility = candidate_data.get('mobilite', 'local').lower()
        
        if mobility in ['remote', 'national'] or 'remote' in location:
            return 'mobile'
        else:
            return 'local'
    
    def _calculate_algorithm_scores(self, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les scores pour chaque algorithme basé sur le contexte
        """
        scores = {}
        
        for algorithm in self.performance_profiles.keys():
            score_details = {
                'volume_score': self._score_volume_fit(algorithm, context),
                'experience_score': self._score_experience_fit(algorithm, context),
                'skills_score': self._score_skills_fit(algorithm, context),
                'performance_score': self._score_performance_fit(algorithm, context),
                'mobility_score': self._score_mobility_fit(algorithm, context)
            }
            
            # Calcul du score total avec pondération
            weights = {
                'volume_score': 0.25,
                'experience_score': 0.20,
                'skills_score': 0.25,
                'performance_score': 0.20,
                'mobility_score': 0.10
            }
            
            total_score = sum(score * weights[criterion] for criterion, score in score_details.items())
            
            score_details['total_score'] = total_score
            scores[algorithm] = score_details
        
        return scores
    
    def _score_volume_fit(self, algorithm: str, context: Dict[str, Any]) -> float:
        """Score basé sur l'adéquation au volume de données"""
        volume_category = context['volume_category']
        volume_rules = self.selection_rules['volume_rules']
        
        # Vérifier si l'algorithme est recommandé pour ce volume
        for vol_cat, vol_rule in volume_rules.items():
            if vol_cat == volume_category:
                if algorithm in vol_rule['recommended']:
                    return 100.0
                else:
                    return 60.0
        
        return 70.0  # Score par défaut
    
    def _score_experience_fit(self, algorithm: str, context: Dict[str, Any]) -> float:
        """Score basé sur l'adéquation au niveau d'expérience"""
        experience_category = context['experience_category']
        experience_rules = self.selection_rules['experience_rules']
        
        if experience_category in experience_rules:
            if algorithm in experience_rules[experience_category]['recommended']:
                return 100.0
            else:
                return 65.0
        
        return 75.0
    
    def _score_skills_fit(self, algorithm: str, context: Dict[str, Any]) -> float:
        """Score basé sur l'adéquation au type de compétences"""
        skills_category = context['skills_category']
        
        if skills_category in self.selection_rules['skills_rules']:
            if algorithm in self.selection_rules['skills_rules'][skills_category]['recommended']:
                return 100.0
            else:
                return 70.0
        
        return 80.0
    
    def _score_performance_fit(self, algorithm: str, context: Dict[str, Any]) -> float:
        """Score basé sur les exigences de performance"""
        performance_priority = context['performance_priority']
        accuracy_priority = context['accuracy_priority']
        
        if algorithm not in self.performance_profiles:
            return 50.0
        
        profile = self.performance_profiles[algorithm]
        
        if performance_priority == 'speed':
            return profile['speed'] * 10
        elif performance_priority == 'accuracy':
            return profile['accuracy'] * 10
        elif performance_priority == 'memory':
            return profile['memory'] * 10
        else:  # balanced
            return (profile['speed'] + profile['accuracy'] + profile['memory']) / 3 * 10
    
    def _score_mobility_fit(self, algorithm: str, context: Dict[str, Any]) -> float:
        """Score basé sur la mobilité géographique"""
        mobility_category = context['mobility_category']
        
        if mobility_category in self.selection_rules['location_rules']:
            if algorithm in self.selection_rules['location_rules'][mobility_category]['recommended']:
                return 100.0
            else:
                return 75.0
        
        return 85.0
    
    def _generate_reasoning(self, context: Dict[str, Any], selected_algorithm: str, 
                          all_scores: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Génère l'explication du choix d'algorithme
        """
        reasoning = []
        selected_scores = all_scores[selected_algorithm]
        
        # Analyse des points forts
        if selected_scores['volume_score'] >= 90:
            reasoning.append(f"Optimal pour {context['volume_category']} volume ({context['jobs_count']} offres)")
        
        if selected_scores['experience_score'] >= 90:
            reasoning.append(f"Adapté aux candidats {context['experience_category']} ({context['candidate_experience']} ans d'exp.)")
        
        if selected_scores['skills_score'] >= 90:
            reasoning.append(f"Optimisé pour les compétences {context['skills_category']}")
        
        if selected_scores['performance_score'] >= 90:
            reasoning.append(f"Excellent équilibre performance/précision")
        
        # Si pas assez de points forts spécifiques, ajouter une raison générale
        if len(reasoning) == 0:
            reasoning.append(f"Meilleur score global ({round(selected_scores['total_score'])}%) pour ce contexte")
        
        return reasoning
    
    def _get_alternatives(self, all_scores: Dict[str, Dict[str, Any]], 
                         selected_algorithm: str) -> List[Dict[str, Any]]:
        """
        Retourne les algorithmes alternatifs
        """
        # Trier par score décroissant et exclure l'algorithme sélectionné
        sorted_algorithms = sorted(
            [(name, scores) for name, scores in all_scores.items() if name != selected_algorithm],
            key=lambda x: x[1]['total_score'],
            reverse=True
        )
        
        alternatives = []
        for name, scores in sorted_algorithms[:3]:  # Top 3 alternatives
            alternatives.append({
                'algorithm': name,
                'score': round(scores['total_score']),
                'reason': f"Score total: {round(scores['total_score'])}%"
            })
        
        return alternatives
    
    def _predict_performance(self, algorithm: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédit les performances attendues
        """
        if algorithm not in self.performance_profiles:
            return {}
        
        profile = self.performance_profiles[algorithm]
        jobs_count = context['jobs_count']
        
        # Estimation du temps de traitement (très approximative)
        base_time = {
            'original': 0.001,
            'enhanced': 0.003,
            'semantic': 0.005,
            'smart-match': 0.002,
            'hybrid': 0.008,
            'custom': 0.002
        }.get(algorithm, 0.003)
        
        estimated_time = base_time * jobs_count
        
        return {
            'estimated_processing_time': round(estimated_time, 3),
            'expected_accuracy': profile['accuracy'] * 10,
            'memory_usage': 'low' if profile['memory'] >= 8 else 'medium' if profile['memory'] >= 6 else 'high',
            'scalability': 'excellent' if profile['speed'] >= 8 else 'good' if profile['speed'] >= 6 else 'moderate'
        }
    
    def get_algorithm_recommendations_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des recommandations d'algorithmes
        """
        return {
            'selection_rules': self.selection_rules,
            'performance_profiles': self.performance_profiles,
            'available_algorithms': list(self.performance_profiles.keys()),
            'recommendation_criteria': [
                'Volume de données',
                'Niveau d\'expérience candidat',
                'Type de compétences',
                'Contraintes de performance',
                'Mobilité géographique'
            ]
        }
