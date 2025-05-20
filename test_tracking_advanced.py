import pytest
import json
from datetime import datetime, timedelta
import uuid
from test_tracking_simulation import TrackingSimulation

class TestTrackingSystem:
    @pytest.fixture
    def tracker(self):
        """Fixture pour créer une instance de TrackingSimulation pour chaque test"""
        return TrackingSimulation()
    
    @pytest.fixture
    def user_with_consent(self, tracker):
        """Fixture pour créer un utilisateur avec consentement"""
        user_id = f"test_user_{uuid.uuid4()}"
        tracker.set_consent(user_id, 'analytics', True)
        return user_id
    
    def test_consent_management(self, tracker):
        """Test de la gestion des consentements"""
        user_id = "test_user_1"
        
        # Vérifier qu'il n'y a pas de consentement par défaut
        assert tracker.check_consent(user_id, 'analytics') == False
        
        # Définir le consentement
        tracker.set_consent(user_id, 'analytics', True)
        assert tracker.check_consent(user_id, 'analytics') == True
        
        # Retirer le consentement
        tracker.set_consent(user_id, 'analytics', False)
        assert tracker.check_consent(user_id, 'analytics') == False
    
    def test_event_tracking_with_consent(self, tracker, user_with_consent):
        """Test du tracking d'événements avec consentement"""
        # Tracker un événement
        event_id = tracker.track_event('test_event', user_with_consent, {'test': 'data'})
        
        # Vérifier que l'événement a été enregistré
        assert len(tracker.events) == 1
        assert tracker.events[0]['event_id'] == event_id
        assert tracker.events[0]['event_type'] == 'test_event'
        assert tracker.events[0]['user_id'] == user_with_consent
        assert tracker.events[0]['data']['test'] == 'data'
    
    def test_event_tracking_without_consent(self, tracker):
        """Test du tracking d'événements sans consentement"""
        user_id = "test_user_no_consent"
        
        # Essayer de tracker un événement sans consentement
        event_id = tracker.track_event('test_event', user_id, {'test': 'data'})
        
        # Vérifier que l'événement n'a pas été enregistré
        assert event_id == False
        assert len(tracker.events) == 0
    
    def test_match_tracking_workflow(self, tracker, user_with_consent):
        """Test du workflow complet de tracking de match"""
        match_id = f"match_{uuid.uuid4()}"
        
        # 1. Proposition de match
        tracker.track_match_proposed(
            user_id=user_with_consent,
            match_id=match_id,
            match_score=85.5,
            match_parameters={"skill_weight": 0.7, "location_weight": 0.3},
            alternatives_count=5,
            constraint_satisfaction={"skills": 0.9, "location": 0.8}
        )
        
        # 2. Visualisation du match
        tracker.track_match_viewed(
            user_id=user_with_consent,
            match_id=match_id,
            view_duration_seconds=45.2,
            view_complete=True
        )
        
        # 3. Décision positive
        tracker.track_match_decision(
            user_id=user_with_consent,
            match_id=match_id,
            accepted=True,
            decision_time_seconds=12.5
        )
        
        # 4. Feedback
        tracker.track_match_feedback(
            user_id=user_with_consent,
            match_id=match_id,
            rating=4,
            feedback_text="Match très pertinent",
            specific_aspects={"relevance": 5, "timing": 3}
        )
        
        # Vérifier que tous les événements ont été correctement enregistrés
        assert len(tracker.events) == 4
        
        # Vérifier les statistiques
        stats = tracker.get_statistics()
        assert stats['unique_matches'] == 1
        assert 'acceptance_rate' in stats
        assert 'average_feedback_rating' in stats
    
    def test_consent_revocation_mid_workflow(self, tracker, user_with_consent):
        """Test du comportement lorsqu'un utilisateur retire son consentement au milieu du workflow"""
        match_id = f"match_{uuid.uuid4()}"
        
        # 1. Proposition de match
        tracker.track_match_proposed(
            user_id=user_with_consent,
            match_id=match_id,
            match_score=85.5,
            match_parameters={"skill_weight": 0.7, "location_weight": 0.3},
            alternatives_count=5,
            constraint_satisfaction={"skills": 0.9, "location": 0.8}
        )
        
        # 2. L'utilisateur retire son consentement
        tracker.set_consent(user_with_consent, 'analytics', False)
        
        # 3. Tentative de tracker un événement après retrait du consentement
        event_id = tracker.track_match_viewed(
            user_id=user_with_consent,
            match_id=match_id,
            view_duration_seconds=45.2,
            view_complete=True
        )
        
        # Vérifier que l'événement n'a pas été enregistré
        assert event_id == False
        assert len(tracker.events) == 1  # Seul le premier événement doit être présent
    
    def test_multi_user_engagement_patterns(self, tracker):
        """Teste différents patterns d'engagement pour plusieurs utilisateurs"""
        # Configurer plusieurs utilisateurs avec différents comportements
        users = {}
        for i in range(5):
            user_id = f"test_user_{i}"
            tracker.set_consent(user_id, 'analytics', True)
            users[user_id] = {
                "engagement_level": i % 3,  # 0=faible, 1=moyen, 2=élevé
                "matches": []
            }
        
        # Simuler des interactions sur plusieurs matches
        for match_num in range(10):
            match_id = f"match_{match_num}"
            
            # Attribuer ce match à certains utilisateurs
            for user_id, user_data in users.items():
                # Simuler différents comportements selon le niveau d'engagement
                if match_num % (3 - user_data["engagement_level"]) == 0:
                    user_data["matches"].append(match_id)
                    
                    # Proposer le match
                    tracker.track_match_proposed(
                        user_id=user_id,
                        match_id=match_id,
                        match_score=75 + user_data["engagement_level"] * 10,
                        match_parameters={"skill_weight": 0.7, "location_weight": 0.3},
                        alternatives_count=3 + user_data["engagement_level"],
                        constraint_satisfaction={"skills": 0.7 + user_data["engagement_level"] * 0.1}
                    )
                    
                    # Simuler visualisation
                    view_complete = user_data["engagement_level"] > 0
                    tracker.track_match_viewed(
                        user_id=user_id,
                        match_id=match_id,
                        view_duration_seconds=10 + user_data["engagement_level"] * 20,
                        view_complete=view_complete
                    )
                    
                    # Simuler décision
                    accepted = user_data["engagement_level"] == 2 or (user_data["engagement_level"] == 1 and match_num % 2 == 0)
                    tracker.track_match_decision(
                        user_id=user_id,
                        match_id=match_id,
                        accepted=accepted,
                        decision_time_seconds=5 + user_data["engagement_level"] * 5
                    )
                    
                    # Simuler feedback pour utilisateurs très engagés
                    if user_data["engagement_level"] == 2 and accepted:
                        tracker.track_match_feedback(
                            user_id=user_id,
                            match_id=match_id,
                            rating=4 + (match_num % 2),
                            feedback_text="Feedback du test"
                        )
        
        # Vérifier les statistiques pour voir si elles reflètent les patterns d'engagement
        stats = tracker.get_statistics()
        
        # Vérifier que les statistiques reflètent correctement les différents niveaux d'engagement
        assert 'acceptance_rate' in stats
        assert 'average_feedback_rating' in stats

    def test_match_feedback_analysis(self, tracker):
        """Test d'analyse approfondie des feedbacks sur les matchs"""
        # Créer un utilisateur avec consentement
        user_id = "test_user_feedback"
        tracker.set_consent(user_id, 'analytics', True)
        
        # Simuler plusieurs feedbacks avec différentes notes
        feedback_data = [
            {"match_id": "match_f1", "rating": 5, "aspects": {"relevance": 5, "timing": 4, "compensation": 5}},
            {"match_id": "match_f2", "rating": 2, "aspects": {"relevance": 1, "timing": 3, "compensation": 4}},
            {"match_id": "match_f3", "rating": 4, "aspects": {"relevance": 4, "timing": 5, "compensation": 3}},
            {"match_id": "match_f4", "rating": 3, "aspects": {"relevance": 3, "timing": 2, "compensation": 4}},
            {"match_id": "match_f5", "rating": 1, "aspects": {"relevance": 1, "timing": 1, "compensation": 2}}
        ]
        
        # Enregistrer tous les feedbacks
        for fb in feedback_data:
            # D'abord simuler une proposition et une décision
            tracker.track_match_proposed(
                user_id=user_id,
                match_id=fb["match_id"],
                match_score=80,
                match_parameters={"skill_weight": 0.7},
                alternatives_count=3,
                constraint_satisfaction={}
            )
            
            tracker.track_match_decision(
                user_id=user_id,
                match_id=fb["match_id"],
                accepted=True,
                decision_time_seconds=10
            )
            
            # Puis enregistrer le feedback
            tracker.track_match_feedback(
                user_id=user_id,
                match_id=fb["match_id"],
                rating=fb["rating"],
                specific_aspects=fb["aspects"]
            )
        
        # Vérifier les statistiques de feedback
        stats = tracker.get_statistics()
        assert 'average_feedback_rating' in stats
        
        # Calculer manuellement la note moyenne attendue (3)
        expected_avg = sum(fb["rating"] for fb in feedback_data) / len(feedback_data)
        assert float(stats['average_feedback_rating'].split('/')[0]) == expected_avg
        
        # Vérifier qu'il y a 5 matches uniques
        assert stats['unique_matches'] == 5


def run_advanced_tests():
    """Exécute les tests avancés en mode standalone"""
    import sys
    
    print("\n=== EXÉCUTION DES TESTS AVANCÉS DU SYSTÈME DE TRACKING ===\n")
    
    # Créer une instance de test
    test_instance = TestTrackingSystem()
    tracker = TrackingSimulation()
    
    # Exécuter chaque test manuellement
    try:
        user_with_consent = f"test_user_{uuid.uuid4()}"
        tracker.set_consent(user_with_consent, 'analytics', True)
        
        print("\n--- Test 1: Gestion des consentements ---")
        test_instance.test_consent_management(tracker)
        print("✓ Test réussi: Gestion des consentements")
        
        print("\n--- Test 2: Tracking d'événements avec consentement ---")
        tracker = TrackingSimulation()  # Réinitialiser
        user_with_consent = f"test_user_{uuid.uuid4()}"
        tracker.set_consent(user_with_consent, 'analytics', True)
        test_instance.test_event_tracking_with_consent(tracker, user_with_consent)
        print("✓ Test réussi: Tracking d'événements avec consentement")
        
        print("\n--- Test 3: Tracking d'événements sans consentement ---")
        tracker = TrackingSimulation()  # Réinitialiser
        test_instance.test_event_tracking_without_consent(tracker)
        print("✓ Test réussi: Tracking d'événements sans consentement")
        
        print("\n--- Test 4: Workflow complet de tracking de match ---")
        tracker = TrackingSimulation()  # Réinitialiser
        user_with_consent = f"test_user_{uuid.uuid4()}"
        tracker.set_consent(user_with_consent, 'analytics', True)
        test_instance.test_match_tracking_workflow(tracker, user_with_consent)
        print("✓ Test réussi: Workflow complet de tracking de match")
        
        print("\n--- Test 5: Révocation de consentement en cours de workflow ---")
        tracker = TrackingSimulation()  # Réinitialiser
        user_with_consent = f"test_user_{uuid.uuid4()}"
        tracker.set_consent(user_with_consent, 'analytics', True)
        test_instance.test_consent_revocation_mid_workflow(tracker, user_with_consent)
        print("✓ Test réussi: Révocation de consentement en cours de workflow")
        
        print("\n--- Test 6: Patterns d'engagement multi-utilisateurs ---")
        tracker = TrackingSimulation()  # Réinitialiser
        test_instance.test_multi_user_engagement_patterns(tracker)
        print("✓ Test réussi: Patterns d'engagement multi-utilisateurs")
        
        print("\n--- Test 7: Analyse des feedbacks ---")
        tracker = TrackingSimulation()  # Réinitialiser
        test_instance.test_match_feedback_analysis(tracker)
        print("✓ Test réussi: Analyse des feedbacks")
        
        print("\n=== TOUS LES TESTS ONT RÉUSSI ===")
        
    except AssertionError as e:
        print(f"❌ ÉCHEC: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_advanced_tests()
