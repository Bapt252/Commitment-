#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tracking_simulator.py

Module contenant la classe de simulation pour le système de tracking.
"""

import uuid
import json
import datetime
import random
from typing import Dict, List, Optional, Any, Union


class TrackingSimulation:
    """
    Classe de simulation pour le système de tracking.
    Permet de simuler la collecte de données et d'événements sans base de données.
    """

    def __init__(self):
        """Initialise la simulation avec des structures de données vides."""
        self.events = []
        self.users = {}
        self.consent_records = {}
        self.feedback_records = []
        self.match_proposals = []
        self.match_views = []
        self.match_decisions = []

    def generate_id(self) -> str:
        """Génère un identifiant unique pour les événements et autres entités."""
        return str(uuid.uuid4())

    def set_user_consent(self, user_id: str, consent_type: str, 
                        is_granted: bool, timestamp: Optional[str] = None) -> Dict:
        """
        Enregistre le consentement d'un utilisateur pour un type spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            consent_type: Type de consentement (analytics, tracking, marketing, etc.)
            is_granted: Si le consentement est accordé ou non
            timestamp: Horodatage de l'action, par défaut l'heure actuelle
            
        Returns:
            Enregistrement du consentement
        """
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        consent_record = {
            "consent_id": self.generate_id(),
            "user_id": user_id,
            "consent_type": consent_type,
            "is_granted": is_granted,
            "timestamp": timestamp
        }
        
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
            
        self.consent_records[user_id][consent_type] = consent_record
        return consent_record

    def check_user_consent(self, user_id: str, consent_type: str) -> bool:
        """
        Vérifie si un utilisateur a donné son consentement pour un type spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            consent_type: Type de consentement à vérifier
            
        Returns:
            True si le consentement est accordé, False sinon
        """
        if user_id not in self.consent_records:
            return False
            
        if consent_type not in self.consent_records[user_id]:
            return False
            
        return self.consent_records[user_id][consent_type]["is_granted"]

    def track_event(self, event_type: str, user_id: str, 
                   data: Dict[str, Any], require_consent: bool = True) -> Optional[Dict]:
        """
        Enregistre un événement dans le système de tracking.
        
        Args:
            event_type: Type d'événement (match_proposed, match_viewed, etc.)
            user_id: Identifiant de l'utilisateur
            data: Données associées à l'événement
            require_consent: Si True, vérifie le consentement utilisateur
            
        Returns:
            Événement enregistré ou None si pas de consentement
        """
        # Vérifier le consentement si nécessaire
        if require_consent and not self.check_user_consent(user_id, "analytics"):
            return None
            
        event_id = self.generate_id()
        timestamp = datetime.datetime.now().isoformat()
        
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": timestamp,
            "data": data
        }
        
        self.events.append(event)
        
        # Traitement spécifique selon le type d'événement
        if event_type == "match_proposed":
            self.match_proposals.append(event)
        elif event_type == "match_viewed":
            self.match_views.append(event)
        elif event_type == "match_decision":
            self.match_decisions.append(event)
        elif event_type == "feedback_submitted":
            self.feedback_records.append(event)
            
        return event

    def track_match_proposed(self, user_id: str, match_id: str, match_score: float,
                            match_parameters: Dict, alternatives_count: int,
                            constraint_satisfaction: Dict) -> Optional[Dict]:
        """
        Enregistre un événement de proposition de match.
        
        Args:
            user_id: Identifiant de l'utilisateur
            match_id: Identifiant du match proposé
            match_score: Score global du match
            match_parameters: Paramètres utilisés pour le matching
            alternatives_count: Nombre d'alternatives considérées
            constraint_satisfaction: Satisfaction des différentes contraintes
            
        Returns:
            Événement enregistré ou None si pas de consentement
        """
        data = {
            "match_id": match_id,
            "match_score": match_score,
            "match_parameters": match_parameters,
            "alternatives_count": alternatives_count,
            "constraint_satisfaction": constraint_satisfaction
        }
        
        return self.track_event("match_proposed", user_id, data)

    def track_match_viewed(self, user_id: str, match_id: str, 
                          view_duration_seconds: float, view_complete: bool) -> Optional[Dict]:
        """
        Enregistre un événement de visualisation de match.
        
        Args:
            user_id: Identifiant de l'utilisateur
            match_id: Identifiant du match visualisé
            view_duration_seconds: Durée de visualisation en secondes
            view_complete: Si la visualisation a été complète
            
        Returns:
            Événement enregistré ou None si pas de consentement
        """
        data = {
            "match_id": match_id,
            "view_duration_seconds": view_duration_seconds,
            "view_complete": view_complete
        }
        
        return self.track_event("match_viewed", user_id, data)

    def track_match_decision(self, user_id: str, match_id: str, 
                            decision: str, decision_time_seconds: float) -> Optional[Dict]:
        """
        Enregistre une décision sur un match (accepté ou refusé).
        
        Args:
            user_id: Identifiant de l'utilisateur
            match_id: Identifiant du match
            decision: 'accepted' ou 'rejected'
            decision_time_seconds: Temps pris pour la décision
            
        Returns:
            Événement enregistré ou None si pas de consentement
        """
        data = {
            "match_id": match_id,
            "decision": decision,
            "decision_time_seconds": decision_time_seconds
        }
        
        return self.track_event("match_decision", user_id, data)

    def track_feedback(self, user_id: str, match_id: str, rating: int, 
                     feedback_text: Optional[str] = None, 
                     specific_aspects: Optional[Dict] = None) -> Optional[Dict]:
        """
        Enregistre un feedback sur un match.
        
        Args:
            user_id: Identifiant de l'utilisateur
            match_id: Identifiant du match
            rating: Note (1-5)
            feedback_text: Texte de feedback libre
            specific_aspects: Notes sur des aspects spécifiques
            
        Returns:
            Événement enregistré ou None si pas de consentement
        """
        data = {
            "match_id": match_id,
            "rating": rating
        }
        
        if feedback_text:
            data["feedback_text"] = feedback_text
            
        if specific_aspects:
            data["specific_aspects"] = specific_aspects
            
        return self.track_event("feedback_submitted", user_id, data)

    def calculate_statistics(self) -> Dict:
        """
        Calcule des statistiques basiques sur les données collectées.
        
        Returns:
            Dictionnaire contenant diverses métriques
        """
        # Calcul du taux d'acceptation
        total_decisions = len(self.match_decisions)
        if total_decisions == 0:
            acceptance_rate = 0
        else:
            acceptances = sum(1 for event in self.match_decisions 
                             if event["data"]["decision"] == "accepted")
            acceptance_rate = acceptances / total_decisions
            
        # Calcul de la note moyenne
        total_feedback = len(self.feedback_records)
        if total_feedback == 0:
            average_rating = 0
        else:
            ratings_sum = sum(event["data"]["rating"] for event in self.feedback_records)
            average_rating = ratings_sum / total_feedback
            
        # Temps moyen de décision
        if total_decisions == 0:
            avg_decision_time = 0
        else:
            decision_times = [event["data"]["decision_time_seconds"] 
                             for event in self.match_decisions]
            avg_decision_time = sum(decision_times) / len(decision_times)
            
        # Distribution des notes
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for event in self.feedback_records:
            rating = event["data"]["rating"]
            if 1 <= rating <= 5:
                rating_distribution[rating] += 1
                
        return {
            "total_events": len(self.events),
            "total_match_proposals": len(self.match_proposals),
            "total_match_views": len(self.match_views),
            "total_decisions": total_decisions,
            "acceptance_rate": acceptance_rate,
            "average_rating": average_rating,
            "avg_decision_time_seconds": avg_decision_time,
            "rating_distribution": rating_distribution
        }

    def __str__(self) -> str:
        """Représentation lisible du système de tracking."""
        stats = self.calculate_statistics()
        
        result = [
            "=== Simulation de Tracking ===",
            f"Nombre total d'événements: {stats['total_events']}",
            f"Nombre de propositions de match: {stats['total_match_proposals']}",
            f"Nombre de visualisations: {stats['total_match_views']}",
            f"Nombre de décisions: {stats['total_decisions']}",
            f"Taux d'acceptation: {stats['acceptance_rate'] * 100:.2f}%",
            f"Note moyenne: {stats['average_rating']:.2f}/5",
            f"Temps moyen de décision: {stats['avg_decision_time_seconds']:.2f} sec",
            "Distribution des notes:",
        ]
        
        for rating, count in stats["rating_distribution"].items():
            result.append(f"  {rating} étoile(s): {count}")
            
        return "\n".join(result)


# Script de démonstration
if __name__ == "__main__":
    # Créer une simulation
    simulation = TrackingSimulation()
    
    # Définir des utilisateurs avec consentement
    users = ["user1", "user2", "user3", "user4", "user5"]
    for user in users:
        # 80% des utilisateurs donnent leur consentement
        consent = random.random() < 0.8
        simulation.set_user_consent(user, "analytics", consent)
    
    # Générer des matchs
    matches = [simulation.generate_id() for _ in range(10)]
    
    # Simuler des événements de matching
    for _ in range(50):
        user = random.choice(users)
        match_id = random.choice(matches)
        
        # Proposer un match
        match_score = random.uniform(0.5, 1.0)
        match_parameters = {
            "skill_weight": 0.7,
            "location_weight": 0.3
        }
        constraint_satisfaction = {
            "skills": random.uniform(0.6, 1.0),
            "location": random.uniform(0.5, 1.0)
        }
        
        simulation.track_match_proposed(
            user, match_id, match_score, 
            match_parameters, 
            random.randint(3, 10),
            constraint_satisfaction
        )
        
        # Visualiser un match (90% des propositions)
        if random.random() < 0.9:
            view_duration = random.uniform(5, 120)
            view_complete = random.random() < 0.7
            
            simulation.track_match_viewed(
                user, match_id, view_duration, view_complete
            )
            
            # Prendre une décision (80% des vues)
            if random.random() < 0.8:
                decision = "accepted" if random.random() < 0.6 else "rejected"
                decision_time = random.uniform(3, 60)
                
                simulation.track_match_decision(
                    user, match_id, decision, decision_time
                )
                
                # Donner un feedback (70% des matches acceptés)
                if decision == "accepted" and random.random() < 0.7:
                    rating = random.randint(1, 5)
                    specific_aspects = {
                        "relevance": random.randint(1, 5),
                        "timing": random.randint(1, 5),
                        "communication": random.randint(1, 5)
                    }
                    
                    simulation.track_feedback(
                        user, match_id, rating,
                        "Ce match correspondait bien à mes attentes",
                        specific_aspects
                    )
    
    # Afficher les statistiques
    print(simulation)

# Assurez-vous que la classe est bien exportée
print("Module tracking_simulator chargé, TrackingSimulation disponible")
