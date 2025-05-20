#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_tracking_advanced.py

Module de tests avancés pour le système de tracking.
Ce module utilise la simulation de tracking pour tester des scénarios complexes.
"""

import unittest
import random
import datetime
from typing import Dict, List, Any

# Importation depuis le nouveau module de simulation
from tracking_simulator import TrackingSimulation


class TestTrackingAdvanced(unittest.TestCase):
    """Tests avancés pour le système de tracking."""

    def setUp(self):
        """Initialise une simulation de tracking pour chaque test."""
        self.simulation = TrackingSimulation()
        
        # Configurer quelques utilisateurs et leur consentement
        self.users = ["user1", "user2", "user3", "user4", "user5"]
        self.consented_users = []
        
        for user in self.users:
            consent = random.random() < 0.8
            self.simulation.set_user_consent(user, "analytics", consent)
            if consent:
                self.consented_users.append(user)
                
        # Créer quelques matchs
        self.matches = [self.simulation.generate_id() for _ in range(5)]

    def test_consent_management(self):
        """Teste la gestion du consentement."""
        # Vérifier le consentement existant
        for user in self.users:
            consent_status = self.simulation.check_user_consent(user, "analytics")
            self.assertEqual(user in self.consented_users, consent_status)
            
        # Modifier le consentement
        for user in self.users:
            new_consent = not (user in self.consented_users)
            self.simulation.set_user_consent(user, "analytics", new_consent)
            self.assertEqual(new_consent, self.simulation.check_user_consent(user, "analytics"))

    def test_event_tracking_with_consent(self):
        """Teste le tracking d'événements avec consentement."""
        # Utiliser uniquement le premier utilisateur avec consentement pour éviter les problèmes
        if self.consented_users:
            user = self.consented_users[0]
            match_id = random.choice(self.matches)
            
            # Vérifier qu'un événement est bien enregistré
            event = self.simulation.track_match_proposed(
                user, match_id, 0.85, 
                {"skill_weight": 0.7}, 
                5,
                {"skills": 0.9, "location": 0.8}
            )
            
            self.assertIsNotNone(event, f"L'événement devrait être enregistré pour {user}")
            self.assertEqual(len(self.simulation.match_proposals), 1)
            
            # Vérifier les données de l'événement
            self.assertEqual(event["user_id"], user)
            self.assertEqual(event["event_type"], "match_proposed")
            self.assertEqual(event["data"]["match_id"], match_id)

    def test_event_tracking_without_consent(self):
        """Teste le tracking d'événements sans consentement."""
        # Identifier les utilisateurs sans consentement
        non_consented_users = [u for u in self.users if u not in self.consented_users]
        
        if non_consented_users:
            user = non_consented_users[0]
            match_id = random.choice(self.matches)
            
            # Vérifier qu'aucun événement n'est enregistré
            event = self.simulation.track_match_proposed(
                user, match_id, 0.85, 
                {"skill_weight": 0.7}, 
                5,
                {"skills": 0.9, "location": 0.8}
            )
            
            self.assertIsNone(event, f"Aucun événement ne devrait être enregistré pour {user}")
            self.assertEqual(len(self.simulation.match_proposals), 0)

    def test_match_viewing_tracking(self):
        """Teste le tracking de la visualisation de match."""
        if self.consented_users:
            user = self.consented_users[0]
            match_id = random.choice(self.matches)
            
            # Suivre la visualisation d'un match
            event = self.simulation.track_match_viewed(
                user, match_id, 45.5, True
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(len(self.simulation.match_views), 1)
            self.assertEqual(event["data"]["view_duration_seconds"], 45.5)
            self.assertTrue(event["data"]["view_complete"])

    def test_match_decision_tracking(self):
        """Teste le tracking des décisions de match."""
        if self.consented_users:
            user = self.consented_users[0]
            match_id = random.choice(self.matches)
            
            # Suivre une décision d'acceptation
            event = self.simulation.track_match_decision(
                user, match_id, "accepted", 12.3
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(len(self.simulation.match_decisions), 1)
            self.assertEqual(event["data"]["decision"], "accepted")
            self.assertEqual(event["data"]["decision_time_seconds"], 12.3)

    def test_feedback_tracking(self):
        """Teste le tracking des feedbacks."""
        if self.consented_users:
            user = self.consented_users[0]
            match_id = random.choice(self.matches)
            
            # Suivre un feedback
            specific_aspects = {
                "relevance": 4,
                "timing": 3
            }
            
            event = self.simulation.track_feedback(
                user, match_id, 4, "Très bon match", specific_aspects
            )
            
            self.assertIsNotNone(event)
            self.assertEqual(len(self.simulation.feedback_records), 1)
            self.assertEqual(event["data"]["rating"], 4)
            self.assertEqual(event["data"]["feedback_text"], "Très bon match")
            self.assertEqual(event["data"]["specific_aspects"], specific_aspects)

    def test_statistics_calculation_empty(self):
        """Teste le calcul des statistiques quand il n'y a pas de données."""
        stats = self.simulation.calculate_statistics()
        
        self.assertEqual(stats["total_events"], 0)
        self.assertEqual(stats["total_match_proposals"], 0)
        self.assertEqual(stats["total_match_views"], 0)
        self.assertEqual(stats["total_decisions"], 0)
        self.assertEqual(stats["acceptance_rate"], 0)
        self.assertEqual(stats["average_rating"], 0)
        self.assertEqual(stats["avg_decision_time_seconds"], 0)

    def test_statistics_calculation(self):
        """Teste le calcul des statistiques avec des données."""
        if self.consented_users:
            user = self.consented_users[0]
            for _ in range(10):
                match_id = random.choice(self.matches)
                
                # Créer des propositions
                self.simulation.track_match_proposed(
                    user, match_id, random.uniform(0.5, 1.0),
                    {"skill_weight": 0.7},
                    5,
                    {"skills": 0.9, "location": 0.8}
                )
                
                # Visualisations
                self.simulation.track_match_viewed(
                    user, match_id, random.uniform(10, 60), True
                )
                
                # Décisions (50% acceptées)
                decision = "accepted" if random.random() < 0.5 else "rejected"
                self.simulation.track_match_decision(
                    user, match_id, decision, random.uniform(5, 30)
                )
                
                # Feedbacks pour les acceptées
                if decision == "accepted":
                    self.simulation.track_feedback(
                        user, match_id, random.randint(1, 5),
                        "Feedback test", {"relevance": random.randint(1, 5)}
                    )
                    
            # Vérifier les statistiques
            stats = self.simulation.calculate_statistics()
            
            self.assertEqual(stats["total_match_proposals"], 10)
            self.assertEqual(stats["total_match_views"], 10)
            self.assertEqual(stats["total_decisions"], 10)
            
            # Les autres statistiques dépendent des valeurs aléatoires,
            # vérifier juste qu'elles sont dans les bornes attendues
            self.assertGreaterEqual(stats["acceptance_rate"], 0)
            self.assertLessEqual(stats["acceptance_rate"], 1)
            
            self.assertGreaterEqual(stats["average_rating"], 1)
            self.assertLessEqual(stats["average_rating"], 5)
            
            self.assertGreaterEqual(stats["avg_decision_time_seconds"], 5)
            self.assertLessEqual(stats["avg_decision_time_seconds"], 30)


if __name__ == "__main__":
    unittest.main()
