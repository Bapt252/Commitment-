"""
Simulateur de comportement utilisateur pour tests de matching ML.

Ce module simule des patterns de comportement utilisateur réalistes pour:
- Tests A/B du système de matching
- Génération de données d'interaction
- Simulation de feedback utilisateur
- Validation des recommandations
"""

import logging
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from ..core.models import CV, JobOffer, MatchResult

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types d'actions utilisateur."""
    VIEW = "view"              # Consultation d'un profil/offre
    LIKE = "like"              # Like/intérêt positif
    DISLIKE = "dislike"        # Dislike/pas intéressé
    APPLY = "apply"            # Candidature/postulation
    SAVE = "save"              # Sauvegarde pour plus tard
    CONTACT = "contact"        # Prise de contact directe
    REJECT = "reject"          # Rejet explicite
    INTERVIEW = "interview"    # Entretien programmé
    HIRE = "hire"              # Embauche finale
    FEEDBACK = "feedback"      # Feedback sur matching


class UserType(Enum):
    """Types d'utilisateurs simulés."""
    RECRUITER = "recruiter"           # Recruteur/RH
    CANDIDATE = "candidate"           # Candidat chercheur d'emploi
    HIRING_MANAGER = "hiring_manager" # Manager en charge du recrutement
    HR_ADMIN = "hr_admin"             # Administrateur RH


@dataclass
class UserAction:
    """Représente une action utilisateur."""
    id: str
    user_id: str
    user_type: UserType
    action_type: ActionType
    target_id: str           # ID du CV ou JobOffer ciblé
    target_type: str         # 'cv' ou 'job_offer'
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionPattern:
    """Définit un pattern d'interaction utilisateur."""
    name: str
    user_type: UserType
    action_weights: Dict[ActionType, float]  # Probabilités d'actions
    session_duration_range: Tuple[int, int]  # Min, max minutes
    actions_per_session_range: Tuple[int, int]  # Min, max actions
    selectivity: float  # 0-1, plus élevé = plus sélectif
    consistency: float  # 0-1, plus élevé = plus cohérent
    fatigue_factor: float  # 0-1, influence de la fatigue sur les actions
    bias_profile: Dict[str, float] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Résultat d'une simulation de comportement."""
    simulation_id: str
    start_time: datetime
    end_time: datetime
    total_actions: int
    actions_by_type: Dict[ActionType, int]
    actions_by_user: Dict[str, List[UserAction]]
    interaction_patterns: List[InteractionPattern]
    summary_stats: Dict[str, Any]
    quality_metrics: Dict[str, float]


class BehaviorSimulator:
    """
    Simulateur de comportement utilisateur pour le système de matching.
    
    Simule des interactions réalistes entre:
    - Candidats et offres d'emploi
    - Recruteurs et CV
    - Patterns de navigation et décision
    """
    
    def __init__(self):
        """Initialise le simulateur de comportement."""
        self.patterns = self._initialize_behavior_patterns()
        self.user_profiles = {}
        self.session_history = []
        
        logger.info("BehaviorSimulator initialized with predefined patterns")
    
    def simulate_user_behavior(self,
                              users: List[Dict[str, Any]],
                              data_items: List[Any],  # CV ou JobOffers
                              duration_days: int = 7,
                              actions_per_user: Optional[int] = None) -> SimulationResult:
        """
        Simule le comportement utilisateur sur une période donnée.
        
        Args:
            users: Liste des utilisateurs à simuler
            data_items: CV ou offres d'emploi disponibles
            duration_days: Durée de simulation en jours
            actions_per_user: Nombre d'actions par utilisateur (optionnel)
            
        Returns:
            SimulationResult avec toutes les actions simulées
        """
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting behavior simulation {simulation_id} for {len(users)} users over {duration_days} days")
        
        all_actions = []
        actions_by_user = defaultdict(list)
        actions_by_type = defaultdict(int)
        
        for user in users:
            user_id = user.get('id', f"user_{random.randint(1000, 9999)}")
            user_type = UserType(user.get('type', 'candidate'))
            
            # Créer un profil utilisateur
            user_profile = self._create_user_profile(user, user_type)
            self.user_profiles[user_id] = user_profile
            
            # Sélectionner un pattern de comportement
            pattern = self._select_behavior_pattern(user_type, user_profile)
            
            # Simuler les actions de cet utilisateur
            user_actions = self._simulate_user_actions(
                user_id, 
                user_type,
                pattern,
                data_items,
                duration_days,
                actions_per_user
            )
            
            all_actions.extend(user_actions)
            actions_by_user[user_id] = user_actions
            
            # Compter les actions par type
            for action in user_actions:
                actions_by_type[action.action_type] += 1
        
        end_time = datetime.now()
        
        # Calculer des métriques de qualité
        quality_metrics = self._calculate_simulation_quality(all_actions, users, data_items)
        
        # Statistiques de résumé
        summary_stats = {
            'total_users': len(users),
            'total_items': len(data_items),
            'average_actions_per_user': len(all_actions) / len(users),
            'simulation_duration_seconds': (end_time - start_time).total_seconds(),
            'actions_per_day': len(all_actions) / duration_days,
            'unique_items_interacted': len(set(action.target_id for action in all_actions))
        }
        
        result = SimulationResult(
            simulation_id=simulation_id,
            start_time=start_time,
            end_time=end_time,
            total_actions=len(all_actions),
            actions_by_type=dict(actions_by_type),
            actions_by_user=dict(actions_by_user),
            interaction_patterns=list(self.patterns.values()),
            summary_stats=summary_stats,
            quality_metrics=quality_metrics
        )
        
        logger.info(f"Simulation {simulation_id} completed: {len(all_actions)} actions generated")
        return result
    
    def simulate_ab_test_behavior(self,
                                group_a_users: List[Dict[str, Any]],
                                group_b_users: List[Dict[str, Any]],
                                data_items: List[Any],
                                test_duration_days: int = 14) -> Dict[str, SimulationResult]:
        """
        Simule le comportement pour un test A/B.
        
        Args:
            group_a_users: Utilisateurs du groupe de contrôle
            group_b_users: Utilisateurs du groupe de test
            data_items: Données communes
            test_duration_days: Durée du test
            
        Returns:
            Dictionnaire avec résultats pour chaque groupe
        """
        logger.info(f"Starting A/B test simulation: {len(group_a_users)} vs {len(group_b_users)} users")
        
        # Simuler groupe A (contrôle)
        result_a = self.simulate_user_behavior(
            group_a_users, 
            data_items, 
            test_duration_days
        )
        
        # Simuler groupe B (test) avec pattern légèrement différent
        # Le groupe B pourrait avoir des patterns modifiés
        result_b = self.simulate_user_behavior(
            group_b_users,
            data_items, 
            test_duration_days
        )
        
        return {
            'group_a': result_a,
            'group_b': result_b
        }
    
    def generate_feedback_data(self,
                              match_results: List[MatchResult],
                              users: List[Dict[str, Any]],
                              feedback_rate: float = 0.3) -> List[Dict[str, Any]]:
        """
        Génère des données de feedback basées sur les résultats de matching.
        
        Args:
            match_results: Résultats de matching à évaluer
            users: Utilisateurs concernés
            feedback_rate: Taux de feedback (0-1)
            
        Returns:
            Liste des feedbacks générés
        """
        logger.info(f"Generating feedback for {len(match_results)} match results")
        
        feedbacks = []
        
        for match in match_results:
            # Probabilité de donner un feedback
            if random.random() > feedback_rate:
                continue
            
            # Trouver l'utilisateur concerné
            user = None
            for u in users:
                if u.get('id') == match.candidate_id or u.get('id') == match.job_id:
                    user = u
                    break
            
            if not user:
                continue
            
            # Simuler un feedback basé sur le score de match
            feedback = self._generate_realistic_feedback(match, user)
            feedbacks.append(feedback)
        
        logger.info(f"Generated {len(feedbacks)} feedback items")
        return feedbacks
    
    def analyze_user_journey(self,
                            user_id: str,
                            actions: List[UserAction]) -> Dict[str, Any]:
        """
        Analyse le parcours d'un utilisateur spécifique.
        
        Args:
            user_id: ID de l'utilisateur
            actions: Actions de l'utilisateur
            
        Returns:
            Analyse détaillée du parcours
        """
        if not actions:
            return {'error': 'No actions found for user'}
        
        # Trier les actions par timestamp
        sorted_actions = sorted(actions, key=lambda a: a.timestamp)
        
        # Analyser les patterns
        session_breaks = self._identify_session_breaks(sorted_actions)
        conversion_funnel = self._analyze_conversion_funnel(sorted_actions)
        engagement_metrics = self._calculate_engagement_metrics(sorted_actions)
        
        journey_analysis = {
            'user_id': user_id,
            'total_actions': len(actions),
            'first_action': sorted_actions[0].timestamp,
            'last_action': sorted_actions[-1].timestamp,
            'total_duration': sorted_actions[-1].timestamp - sorted_actions[0].timestamp,
            'session_count': len(session_breaks) + 1,
            'actions_by_type': defaultdict(int),
            'conversion_funnel': conversion_funnel,
            'engagement_metrics': engagement_metrics,
            'behavioral_patterns': self._identify_behavioral_patterns(sorted_actions)
        }
        
        # Compter les actions par type
        for action in actions:
            journey_analysis['actions_by_type'][action.action_type] += 1
        
        journey_analysis['actions_by_type'] = dict(journey_analysis['actions_by_type'])
        
        return journey_analysis
    
    # Méthodes privées
    
    def _initialize_behavior_patterns(self) -> Dict[str, InteractionPattern]:
        """Initialise les patterns de comportement prédéfinis."""
        patterns = {}
        
        # Pattern candidat actif
        patterns['active_candidate'] = InteractionPattern(
            name="Active Job Seeker",
            user_type=UserType.CANDIDATE,
            action_weights={
                ActionType.VIEW: 0.4,
                ActionType.LIKE: 0.2,
                ActionType.APPLY: 0.15,
                ActionType.SAVE: 0.15,
                ActionType.CONTACT: 0.05,
                ActionType.DISLIKE: 0.05
            },
            session_duration_range=(15, 60),
            actions_per_session_range=(5, 25),
            selectivity=0.6,
            consistency=0.8,
            fatigue_factor=0.3
        )
        
        # Pattern candidat passif
        patterns['passive_candidate'] = InteractionPattern(
            name="Passive Job Browser",
            user_type=UserType.CANDIDATE,
            action_weights={
                ActionType.VIEW: 0.6,
                ActionType.LIKE: 0.1,
                ActionType.APPLY: 0.05,
                ActionType.SAVE: 0.2,
                ActionType.CONTACT: 0.02,
                ActionType.DISLIKE: 0.03
            },
            session_duration_range=(5, 30),
            actions_per_session_range=(2, 10),
            selectivity=0.8,
            consistency=0.6,
            fatigue_factor=0.5
        )
        
        # Pattern recruteur expérimenté
        patterns['experienced_recruiter'] = InteractionPattern(
            name="Experienced Recruiter",
            user_type=UserType.RECRUITER,
            action_weights={
                ActionType.VIEW: 0.3,
                ActionType.LIKE: 0.15,
                ActionType.CONTACT: 0.2,
                ActionType.SAVE: 0.15,
                ActionType.REJECT: 0.1,
                ActionType.INTERVIEW: 0.08,
                ActionType.HIRE: 0.02
            },
            session_duration_range=(20, 120),
            actions_per_session_range=(10, 50),
            selectivity=0.7,
            consistency=0.9,
            fatigue_factor=0.2
        )
        
        # Pattern recruteur novice
        patterns['novice_recruiter'] = InteractionPattern(
            name="Novice Recruiter",
            user_type=UserType.RECRUITER,
            action_weights={
                ActionType.VIEW: 0.5,
                ActionType.LIKE: 0.2,
                ActionType.CONTACT: 0.1,
                ActionType.SAVE: 0.15,
                ActionType.REJECT: 0.03,
                ActionType.INTERVIEW: 0.02
            },
            session_duration_range=(10, 60),
            actions_per_session_range=(5, 20),
            selectivity=0.4,
            consistency=0.5,
            fatigue_factor=0.6
        )
        
        # Pattern hiring manager
        patterns['hiring_manager'] = InteractionPattern(
            name="Hiring Manager",
            user_type=UserType.HIRING_MANAGER,
            action_weights={
                ActionType.VIEW: 0.4,
                ActionType.LIKE: 0.1,
                ActionType.CONTACT: 0.15,
                ActionType.INTERVIEW: 0.2,
                ActionType.HIRE: 0.1,
                ActionType.REJECT: 0.05
            },
            session_duration_range=(30, 90),
            actions_per_session_range=(3, 15),
            selectivity=0.9,
            consistency=0.85,
            fatigue_factor=0.1
        )
        
        return patterns
    
    def _create_user_profile(self, user: Dict[str, Any], user_type: UserType) -> Dict[str, Any]:
        """Crée un profil utilisateur détaillé."""
        base_profile = {
            'id': user.get('id'),
            'type': user_type,
            'experience_level': random.choice(['junior', 'mid', 'senior']),
            'industry_focus': random.choice(['tech', 'finance', 'retail', 'healthcare']),
            'activity_level': random.choice(['low', 'medium', 'high']),
            'decision_speed': random.uniform(0.3, 1.0),  # 0=lent, 1=rapide
            'risk_tolerance': random.uniform(0.2, 0.9),  # 0=conservateur, 1=risque
            'tech_savviness': random.uniform(0.4, 1.0),  # 0=basique, 1=expert
        }
        
        # Ajouter des caractéristiques spécifiques selon le type
        if user_type == UserType.CANDIDATE:
            base_profile.update({
                'job_search_urgency': random.uniform(0.1, 1.0),
                'salary_flexibility': random.uniform(0.3, 0.8),
                'location_flexibility': random.uniform(0.2, 0.9)
            })
        elif user_type in [UserType.RECRUITER, UserType.HIRING_MANAGER]:
            base_profile.update({
                'hiring_pressure': random.uniform(0.3, 0.9),
                'candidate_standards': random.uniform(0.5, 0.95),
                'budget_constraints': random.uniform(0.4, 0.8)
            })
        
        return base_profile
    
    def _select_behavior_pattern(self, user_type: UserType, profile: Dict[str, Any]) -> InteractionPattern:
        """Sélectionne un pattern de comportement basé sur le profil utilisateur."""
        # Filtrer les patterns par type d'utilisateur
        matching_patterns = [p for p in self.patterns.values() if p.user_type == user_type]
        
        if not matching_patterns:
            # Pattern par défaut
            return list(self.patterns.values())[0]
        
        # Sélectionner basé sur le niveau d'activité
        activity_level = profile.get('activity_level', 'medium')
        
        if user_type == UserType.CANDIDATE:
            if activity_level == 'high':
                return self.patterns.get('active_candidate', matching_patterns[0])
            else:
                return self.patterns.get('passive_candidate', matching_patterns[0])
        
        elif user_type == UserType.RECRUITER:
            experience = profile.get('experience_level', 'mid')
            if experience == 'senior':
                return self.patterns.get('experienced_recruiter', matching_patterns[0])
            else:
                return self.patterns.get('novice_recruiter', matching_patterns[0])
        
        elif user_type == UserType.HIRING_MANAGER:
            return self.patterns.get('hiring_manager', matching_patterns[0])
        
        return matching_patterns[0]
    
    def _simulate_user_actions(self,
                              user_id: str,
                              user_type: UserType,
                              pattern: InteractionPattern,
                              data_items: List[Any],
                              duration_days: int,
                              actions_per_user: Optional[int]) -> List[UserAction]:
        """Simule les actions d'un utilisateur spécifique."""
        actions = []
        
        # Déterminer le nombre total d'actions
        if actions_per_user:
            total_actions = actions_per_user
        else:
            # Calculer basé sur le pattern et la durée
            avg_sessions = duration_days * random.uniform(0.5, 2.0)
            avg_actions_per_session = sum(pattern.actions_per_session_range) / 2
            total_actions = int(avg_sessions * avg_actions_per_session)
        
        # Générer les actions
        current_time = datetime.now() - timedelta(days=duration_days)
        
        for i in range(total_actions):
            # Sélectionner le type d'action basé sur les poids
            action_type = self._weighted_random_choice(pattern.action_weights)
            
            # Sélectionner un item cible
            target_item = self._select_target_item(
                data_items, 
                user_type, 
                pattern,
                actions  # Historique pour éviter les répétitions
            )
            
            if not target_item:
                continue
            
            # Déterminer le type de cible
            target_type = 'cv' if hasattr(target_item, 'skills') else 'job_offer'
            
            # Calculer le timestamp (avec progression temporelle)
            time_offset = (duration_days * (i / total_actions)) * 24 * 3600
            action_time = current_time + timedelta(seconds=time_offset)
            
            # Ajouter de la variation temporelle réaliste
            action_time += timedelta(minutes=random.randint(-30, 30))
            
            # Créer l'action
            action = UserAction(
                id=f"action_{user_id}_{i}",
                user_id=user_id,
                user_type=user_type,
                action_type=action_type,
                target_id=target_item.id,
                target_type=target_type,
                timestamp=action_time,
                context={
                    'session_id': f"session_{user_id}_{i // 10}",  # Grouper par sessions
                    'position_in_session': i % 10,
                    'pattern_name': pattern.name
                },
                metadata={
                    'simulated': True,
                    'pattern_applied': pattern.name,
                    'selectivity_score': pattern.selectivity,
                    'fatigue_factor': max(0, 1 - (i / total_actions) * pattern.fatigue_factor)
                }
            )
            
            actions.append(action)
        
        return actions
    
    def _weighted_random_choice(self, weights: Dict[ActionType, float]) -> ActionType:
        """Sélection aléatoire pondérée d'un type d'action."""
        choices = list(weights.keys())
        probabilities = list(weights.values())
        
        # Normaliser les probabilités
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        return np.random.choice(choices, p=probabilities)
    
    def _select_target_item(self,
                           data_items: List[Any],
                           user_type: UserType,
                           pattern: InteractionPattern,
                           action_history: List[UserAction]) -> Optional[Any]:
        """Sélectionne un item cible basé sur le comportement utilisateur."""
        if not data_items:
            return None
        
        # Éviter les répétitions récentes
        recent_targets = set()
        if len(action_history) > 10:
            recent_targets = {a.target_id for a in action_history[-10:]}
        
        # Filtrer les items disponibles
        available_items = [item for item in data_items if item.id not in recent_targets]
        
        if not available_items:
            available_items = data_items  # Si tout a été vu, reset
        
        # Sélection basée sur la sélectivité du pattern
        if random.random() < pattern.selectivity:
            # Sélection sélective (préférer certains critères)
            return self._selective_item_choice(available_items, user_type, pattern)
        else:
            # Sélection aléatoire
            return random.choice(available_items)
    
    def _selective_item_choice(self,
                              items: List[Any],
                              user_type: UserType,
                              pattern: InteractionPattern) -> Any:
        """Sélection d'item basée sur des critères sélectifs."""
        # Scorer les items selon leur pertinence pour l'utilisateur
        scored_items = []
        
        for item in items:
            score = random.uniform(0.1, 1.0)  # Score de base aléatoire
            
            # Ajuster selon le type d'utilisateur
            if user_type == UserType.CANDIDATE and hasattr(item, 'company'):
                # Les candidats préfèrent certaines entreprises/secteurs
                if hasattr(item, 'sector'):
                    preferred_sectors = ['technology', 'finance']
                    if getattr(item, 'sector', None) in preferred_sectors:
                        score *= 1.2
            
            elif user_type in [UserType.RECRUITER, UserType.HIRING_MANAGER]:
                if hasattr(item, 'skills'):
                    # Les recruteurs préfèrent des profils avec plus de compétences
                    skill_count = len(getattr(item, 'skills', []))
                    score *= (1 + skill_count / 20)  # Bonus pour plus de compétences
            
            scored_items.append((item, score))
        
        # Trier et sélectionner parmi les meilleurs
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Sélection pondérée parmi le top 30%
        top_items = scored_items[:max(1, len(scored_items) // 3)]
        
        return random.choice(top_items)[0]
    
    def _generate_realistic_feedback(self,
                                   match: MatchResult,
                                   user: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un feedback réaliste basé sur un match."""
        # Le feedback dépend du score de match et du profil utilisateur
        base_satisfaction = match.score
        
        # Ajouter du bruit réaliste
        noise = random.gauss(0, 0.1)
        satisfaction = max(0, min(1, base_satisfaction + noise))
        
        # Déterminer le type de feedback
        if satisfaction > 0.8:
            feedback_type = 'very_positive'
            rating = 5
        elif satisfaction > 0.6:
            feedback_type = 'positive'
            rating = 4
        elif satisfaction > 0.4:
            feedback_type = 'neutral'
            rating = 3
        elif satisfaction > 0.2:
            feedback_type = 'negative'
            rating = 2
        else:
            feedback_type = 'very_negative'
            rating = 1
        
        # Générer commentaire
        comments = {
            'very_positive': ["Excellent match!", "Perfect fit for our needs", "Great recommendation"],
            'positive': ["Good match", "Interesting profile", "Worth considering"],
            'neutral': ["Okay match", "Could be better", "Average recommendation"],
            'negative': ["Not a good fit", "Missing key requirements", "Poor match"],
            'very_negative': ["Terrible match", "Completely irrelevant", "Waste of time"]
        }
        
        feedback = {
            'id': f"feedback_{match.candidate_id}_{match.job_id}",
            'match_id': f"{match.candidate_id}_{match.job_id}",
            'user_id': user.get('id'),
            'rating': rating,
            'satisfaction': satisfaction,
            'feedback_type': feedback_type,
            'comment': random.choice(comments[feedback_type]),
            'timestamp': datetime.now(),
            'metadata': {
                'original_score': match.score,
                'score_adjustment': satisfaction - base_satisfaction,
                'simulated': True
            }
        }
        
        return feedback
    
    def _identify_session_breaks(self, actions: List[UserAction]) -> List[int]:
        """Identifie les pauses entre sessions dans la liste d'actions."""
        if len(actions) < 2:
            return []
        
        breaks = []
        session_gap_threshold = timedelta(hours=1)  # Pause > 1h = nouvelle session
        
        for i in range(1, len(actions)):
            time_gap = actions[i].timestamp - actions[i-1].timestamp
            if time_gap > session_gap_threshold:
                breaks.append(i)
        
        return breaks
    
    def _analyze_conversion_funnel(self, actions: List[UserAction]) -> Dict[str, int]:
        """Analyse le funnel de conversion des actions."""
        funnel = {
            'awareness': 0,      # VIEW actions
            'interest': 0,       # LIKE, SAVE actions
            'consideration': 0,  # CONTACT actions
            'conversion': 0      # APPLY, HIRE actions
        }
        
        for action in actions:
            if action.action_type == ActionType.VIEW:
                funnel['awareness'] += 1
            elif action.action_type in [ActionType.LIKE, ActionType.SAVE]:
                funnel['interest'] += 1
            elif action.action_type == ActionType.CONTACT:
                funnel['consideration'] += 1
            elif action.action_type in [ActionType.APPLY, ActionType.HIRE]:
                funnel['conversion'] += 1
        
        return funnel
    
    def _calculate_engagement_metrics(self, actions: List[UserAction]) -> Dict[str, float]:
        """Calcule des métriques d'engagement utilisateur."""
        if not actions:
            return {}
        
        # Durée totale
        total_duration = actions[-1].timestamp - actions[0].timestamp
        
        # Nombre de sessions
        session_breaks = self._identify_session_breaks(actions)
        num_sessions = len(session_breaks) + 1
        
        # Actions par session
        actions_per_session = len(actions) / num_sessions
        
        # Taux d'interaction (actions non-view / total)
        non_view_actions = sum(1 for a in actions if a.action_type != ActionType.VIEW)
        interaction_rate = non_view_actions / len(actions)
        
        # Consistance temporelle (variance des gaps entre actions)
        time_gaps = []
        for i in range(1, len(actions)):
            gap = (actions[i].timestamp - actions[i-1].timestamp).total_seconds()
            time_gaps.append(gap)
        
        consistency = 1 - (np.std(time_gaps) / np.mean(time_gaps)) if time_gaps else 0
        consistency = max(0, min(1, consistency))
        
        return {
            'total_duration_hours': total_duration.total_seconds() / 3600,
            'num_sessions': num_sessions,
            'actions_per_session': actions_per_session,
            'interaction_rate': interaction_rate,
            'temporal_consistency': consistency,
            'average_session_gap_hours': np.mean([gap / 3600 for gap in time_gaps]) if time_gaps else 0
        }
    
    def _identify_behavioral_patterns(self, actions: List[UserAction]) -> List[str]:
        """Identifie les patterns comportementaux dans les actions."""
        patterns = []
        
        if not actions:
            return patterns
        
        # Pattern: Navigation extensive
        if len(actions) > 50:
            patterns.append('extensive_browser')
        
        # Pattern: Décision rapide
        view_to_action_times = []
        for i in range(len(actions) - 1):
            if (actions[i].action_type == ActionType.VIEW and 
                actions[i+1].action_type != ActionType.VIEW and
                actions[i].target_id == actions[i+1].target_id):
                time_diff = (actions[i+1].timestamp - actions[i].timestamp).total_seconds()
                view_to_action_times.append(time_diff)
        
        if view_to_action_times and np.mean(view_to_action_times) < 60:  # Moins de 1 minute
            patterns.append('quick_decision_maker')
        
        # Pattern: Sélectivité élevée
        unique_targets = len(set(a.target_id for a in actions))
        action_types = set(a.action_type for a in actions)
        
        if len(action_types) <= 3 and ActionType.VIEW in action_types:
            patterns.append('selective_browser')
        
        # Pattern: Très actif
        total_duration = actions[-1].timestamp - actions[0].timestamp
        if total_duration.total_seconds() > 0:
            actions_per_hour = len(actions) / (total_duration.total_seconds() / 3600)
            if actions_per_hour > 10:
                patterns.append('highly_active')
        
        # Pattern: Comparateur
        if unique_targets / len(actions) > 0.7:  # Beaucoup d'items différents consultés
            patterns.append('comparison_shopper')
        
        return patterns
    
    def _calculate_simulation_quality(self,
                                    actions: List[UserAction],
                                    users: List[Dict[str, Any]],
                                    data_items: List[Any]) -> Dict[str, float]:
        """Calcule des métriques de qualité de la simulation."""
        if not actions:
            return {'overall_quality': 0.0}
        
        metrics = {}
        
        # Diversité des actions
        action_types = [a.action_type for a in actions]
        unique_action_types = len(set(action_types))
        action_diversity = unique_action_types / len(ActionType)
        metrics['action_diversity'] = action_diversity
        
        # Couverture des données
        unique_targets = len(set(a.target_id for a in actions))
        data_coverage = unique_targets / len(data_items) if data_items else 0
        metrics['data_coverage'] = min(1.0, data_coverage)
        
        # Distribution temporelle
        if len(actions) > 1:
            timestamps = [a.timestamp for a in actions]
            time_span = max(timestamps) - min(timestamps)
            if time_span.total_seconds() > 0:
                temporal_distribution = len(set(t.date() for t in timestamps)) / (time_span.days + 1)
                metrics['temporal_distribution'] = min(1.0, temporal_distribution)
            else:
                metrics['temporal_distribution'] = 0.0
        else:
            metrics['temporal_distribution'] = 1.0
        
        # Réalisme comportemental (basé sur les patterns)
        realistic_sequences = 0
        total_sequences = 0
        
        for i in range(len(actions) - 1):
            current = actions[i]
            next_action = actions[i+1]
            
            # Vérifier si la séquence est réaliste
            if self._is_realistic_sequence(current, next_action):
                realistic_sequences += 1
            total_sequences += 1
        
        behavioral_realism = realistic_sequences / total_sequences if total_sequences > 0 else 1.0
        metrics['behavioral_realism'] = behavioral_realism
        
        # Équilibre utilisateur
        actions_per_user = defaultdict(int)
        for action in actions:
            actions_per_user[action.user_id] += 1
        
        if len(actions_per_user) > 0:
            user_balance = 1 - (np.std(list(actions_per_user.values())) / np.mean(list(actions_per_user.values())))
            metrics['user_balance'] = max(0, min(1, user_balance))
        else:
            metrics['user_balance'] = 1.0
        
        # Score global
        overall_quality = np.mean(list(metrics.values()))
        metrics['overall_quality'] = overall_quality
        
        return metrics
    
    def _is_realistic_sequence(self, action1: UserAction, action2: UserAction) -> bool:
        """Vérifie si une séquence d'actions est réaliste."""
        # Séquences courantes réalistes
        realistic_sequences = [
            (ActionType.VIEW, ActionType.LIKE),
            (ActionType.VIEW, ActionType.SAVE),
            (ActionType.VIEW, ActionType.APPLY),
            (ActionType.LIKE, ActionType.CONTACT),
            (ActionType.LIKE, ActionType.APPLY),
            (ActionType.SAVE, ActionType.VIEW),  # Revoir un item sauvé
            (ActionType.CONTACT, ActionType.INTERVIEW),
            (ActionType.INTERVIEW, ActionType.HIRE),
            (ActionType.VIEW, ActionType.DISLIKE),
            (ActionType.VIEW, ActionType.REJECT)
        ]
        
        # Même utilisateur et même cible pour certaines séquences
        if action1.user_id == action2.user_id and action1.target_id == action2.target_id:
            sequence = (action1.action_type, action2.action_type)
            return sequence in realistic_sequences
        
        # Séquences différentes cibles (navigation)
        return action1.action_type == ActionType.VIEW or action2.action_type == ActionType.VIEW
