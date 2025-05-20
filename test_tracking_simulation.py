import json
from datetime import datetime
import uuid

class TrackingSimulation:
    """
    Simulation du système de tracking pour montrer le fonctionnement sans modifier la base de données
    """
    
    def __init__(self):
        self.events = []
        self.consents = {}
        print("Système de tracking initialisé")
        
    def set_consent(self, user_id, consent_type, is_granted):
        """Définit le consentement d'un utilisateur"""
        if user_id not in self.consents:
            self.consents[user_id] = {}
            
        self.consents[user_id][consent_type] = {
            'granted': is_granted,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Consentement '{consent_type}' pour utilisateur '{user_id}': {is_granted}")
        return True
        
    def check_consent(self, user_id, consent_type):
        """Vérifie si l'utilisateur a donné son consentement"""
        if user_id not in self.consents:
            return False
            
        if consent_type not in self.consents[user_id]:
            return False
            
        return self.consents[user_id][consent_type]['granted']
        
    def track_event(self, event_type, user_id, data=None):
        """Enregistre un événement utilisateur"""
        if not self.check_consent(user_id, 'analytics'):
            print(f"⚠️ Événement ignoré - pas de consentement pour utilisateur '{user_id}'")
            return False
            
        event_id = f"evt_{uuid.uuid4()}"
        event = {
            'event_id': event_id,
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        
        self.events.append(event)
        print(f"✅ Événement '{event_type}' enregistré pour '{user_id}'")
        return event_id
        
    def track_match_proposed(self, user_id, match_id, match_score, match_parameters, alternatives_count, constraint_satisfaction):
        """Suit un événement de match proposé"""
        data = {
            'match_id': match_id,
            'match_score': match_score,
            'match_parameters': match_parameters,
            'alternatives_count': alternatives_count,
            'constraint_satisfaction': constraint_satisfaction
        }
        return self.track_event('match_proposed', user_id, data)
        
    def track_match_viewed(self, user_id, match_id, view_duration_seconds, view_complete):
        """Suit un événement de visualisation de match"""
        data = {
            'match_id': match_id,
            'view_duration_seconds': view_duration_seconds,
            'view_complete': view_complete
        }
        return self.track_event('match_viewed', user_id, data)
        
    def track_match_decision(self, user_id, match_id, accepted, decision_time_seconds, reasons=None):
        """Suit un événement de décision (acceptation/refus)"""
        event_type = 'match_accepted' if accepted else 'match_rejected'
        data = {
            'match_id': match_id,
            'decision_time_seconds': decision_time_seconds
        }
        if reasons:
            data['reasons'] = reasons
            
        return self.track_event(event_type, user_id, data)
        
    def track_match_feedback(self, user_id, match_id, rating, feedback_text=None, specific_aspects=None):
        """Suit un événement de feedback"""
        data = {
            'match_id': match_id,
            'rating': rating
        }
        if feedback_text:
            data['feedback_text'] = feedback_text
        if specific_aspects:
            data['specific_aspects'] = specific_aspects
            
        return self.track_event('match_feedback', user_id, data)
        
    def get_statistics(self):
        """Calcule des statistiques basiques sur les événements collectés"""
        if not self.events:
            return "Aucun événement collecté"
            
        event_types = {}
        users = set()
        matches = set()
        
        for event in self.events:
            event_type = event['event_type']
            users.add(event['user_id'])
            
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
            
            if 'data' in event and 'match_id' in event['data']:
                matches.add(event['data']['match_id'])
                
        stats = {
            'total_events': len(self.events),
            'unique_users': len(users),
            'unique_matches': len(matches),
            'event_distribution': event_types
        }
        
        # Calculer le taux d'acceptation si possible
        if 'match_accepted' in event_types and 'match_rejected' in event_types:
            total_decisions = event_types.get('match_accepted', 0) + event_types.get('match_rejected', 0)
            if total_decisions > 0:
                acceptance_rate = (event_types.get('match_accepted', 0) / total_decisions) * 100
                stats['acceptance_rate'] = f"{acceptance_rate:.1f}%"
                
        # Calculer la note moyenne de feedback si possible
        feedback_events = [e for e in self.events if e['event_type'] == 'match_feedback']
        if feedback_events:
            avg_rating = sum(e['data'].get('rating', 0) for e in feedback_events) / len(feedback_events)
            stats['average_feedback_rating'] = f"{avg_rating:.1f}/5"
            
        return stats
        
    def print_events(self):
        """Affiche tous les événements collectés"""
        if not self.events:
            print("Aucun événement collecté")
            return
            
        print("\n=== Événements collectés ===")
        for i, event in enumerate(self.events):
            print(f"{i+1}. Type: {event['event_type']}, User: {event['user_id']}, Time: {event['timestamp']}")
            print(f"   Data: {json.dumps(event['data'], indent=2)}")
            print()


# Démonstration du système de tracking
def run_demo():
    print("\n=== DÉMONSTRATION DU SYSTÈME DE TRACKING ===\n")
    
    tracker = TrackingSimulation()
    
    # Utilisateurs de test
    user1 = "user_123"
    user2 = "user_456"
    
    # Test 1: Événement sans consentement
    print("\n--- Test 1: Événement sans consentement ---")
    tracker.track_match_proposed(
        user_id=user1,
        match_id="match_001",
        match_score=85.5,
        match_parameters={"skill_weight": 0.7, "location_weight": 0.3},
        alternatives_count=5,
        constraint_satisfaction={"skills": 0.9, "location": 0.8}
    )
    
    # Test 2: Définir le consentement et suivre les événements
    print("\n--- Test 2: Événements avec consentement ---")
    tracker.set_consent(user1, 'analytics', True)
    
    tracker.track_match_proposed(
        user_id=user1,
        match_id="match_001",
        match_score=85.5,
        match_parameters={"skill_weight": 0.7, "location_weight": 0.3},
        alternatives_count=5,
        constraint_satisfaction={"skills": 0.9, "location": 0.8}
    )
    
    tracker.track_match_viewed(
        user_id=user1,
        match_id="match_001",
        view_duration_seconds=45.2,
        view_complete=True
    )
    
    tracker.track_match_decision(
        user_id=user1,
        match_id="match_001",
        accepted=True,
        decision_time_seconds=12.5
    )
    
    tracker.track_match_feedback(
        user_id=user1,
        match_id="match_001",
        rating=4,
        feedback_text="Ce match était très pertinent pour mes compétences",
        specific_aspects={"relevance": 5, "timing": 3}
    )
    
    # Test 3: Multiple utilisateurs et matches
    print("\n--- Test 3: Multiple utilisateurs et matches ---")
    tracker.set_consent(user2, 'analytics', True)
    
    # Premier match pour user2
    tracker.track_match_proposed(
        user_id=user2,
        match_id="match_002",
        match_score=72.3,
        match_parameters={"skill_weight": 0.6, "location_weight": 0.4},
        alternatives_count=3,
        constraint_satisfaction={"skills": 0.7, "location": 0.9}
    )
    
    tracker.track_match_viewed(
        user_id=user2,
        match_id="match_002",
        view_duration_seconds=30.5,
        view_complete=True
    )
    
    tracker.track_match_decision(
        user_id=user2,
        match_id="match_002",
        accepted=False,
        decision_time_seconds=8.2,
        reasons=["not_interested", "skills_mismatch"]
    )
    
    # Deuxième match pour user2
    tracker.track_match_proposed(
        user_id=user2,
        match_id="match_003",
        match_score=92.1,
        match_parameters={"skill_weight": 0.8, "location_weight": 0.2},
        alternatives_count=7,
        constraint_satisfaction={"skills": 0.95, "location": 0.85}
    )
    
    tracker.track_match_viewed(
        user_id=user2,
        match_id="match_003",
        view_duration_seconds=68.7,
        view_complete=True
    )
    
    tracker.track_match_decision(
        user_id=user2,
        match_id="match_003",
        accepted=True,
        decision_time_seconds=15.3
    )
    
    tracker.track_match_feedback(
        user_id=user2,
        match_id="match_003",
        rating=5,
        feedback_text="Match parfait pour mes compétences et aspirations",
        specific_aspects={"relevance": 5, "timing": 5, "compensation": 4}
    )
    
    # Afficher tous les événements collectés
    tracker.print_events()
    
    # Afficher les statistiques
    print("\n=== Statistiques ===")
    stats = tracker.get_statistics()
    print(json.dumps(stats, indent=2))
    
    print("\n=== FIN DE LA DÉMONSTRATION ===")
    print("Cette simulation montre comment le système de tracking fonctionnerait en production.")
    print("Les données seraient stockées dans la base de données et visualisées dans Grafana.")

if __name__ == "__main__":
    run_demo()
