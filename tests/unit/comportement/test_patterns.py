import pytest
from datetime import datetime, timedelta
from user_behavior.patterns.sequence_detection import PatternDetector


def test_detect_patterns():
    # Test de la détection de patterns
    detector = PatternDetector(window_size=7, min_occurrences=2)
    
    # Créer des données de test
    now = datetime.now()
    
    # Actions utilisateur simulées
    user_actions = [
        # Utilisateur 1 - Motif quotidien
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(days=5)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=5, hours=1)).isoformat()},
        {'user_id': 'user1', 'action_type': 'logout', 'timestamp': (now - timedelta(days=5, hours=2)).isoformat()},
        
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(days=4)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=4, hours=1)).isoformat()},
        {'user_id': 'user1', 'action_type': 'logout', 'timestamp': (now - timedelta(days=4, hours=2)).isoformat()},
        
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(days=3)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=3, hours=1)).isoformat()},
        {'user_id': 'user1', 'action_type': 'logout', 'timestamp': (now - timedelta(days=3, hours=2)).isoformat()},
        
        # Utilisateur 2 - Motif hebdomadaire
        {'user_id': 'user2', 'action_type': 'login', 'timestamp': (now - timedelta(days=7)).isoformat()},
        {'user_id': 'user2', 'action_type': 'apply_job', 'timestamp': (now - timedelta(days=7, hours=1)).isoformat()},
        
        {'user_id': 'user2', 'action_type': 'login', 'timestamp': now.isoformat()},
        {'user_id': 'user2', 'action_type': 'apply_job', 'timestamp': (now - timedelta(hours=1)).isoformat()}
    ]
    
    # Détecter les patterns
    patterns = detector.detect_patterns(user_actions)
    
    # Vérifier que les patterns ont été détectés pour les deux utilisateurs
    assert 'user1' in patterns
    assert 'user2' in patterns
    
    # Vérifier les patterns de séquence pour l'utilisateur 1
    user1_patterns = patterns['user1']
    assert 'sequence_patterns' in user1_patterns
    assert 'login > view_job' in user1_patterns['sequence_patterns'].get('bigrams', [])
    assert 'view_job > logout' in user1_patterns['sequence_patterns'].get('bigrams', [])
    
    # Vérifier les patterns de temps pour l'utilisateur 1
    assert 'time_patterns' in user1_patterns
    
    # Vérifier les patterns d'intervalle pour l'utilisateur 2
    user2_patterns = patterns['user2']
    assert 'interval_patterns' in user2_patterns


def test_get_common_patterns():
    # Test des patterns communs
    detector = PatternDetector(window_size=7, min_occurrences=2)
    
    # Créer des données de test avec des patterns communs
    now = datetime.now()
    
    # Actions utilisateur simulées
    user_actions = [
        # Trois utilisateurs avec le même pattern le matin
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(days=1, hours=8)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=1, hours=9)).isoformat()},
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(hours=8)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(hours=9)).isoformat()},
        
        {'user_id': 'user2', 'action_type': 'login', 'timestamp': (now - timedelta(days=1, hours=7)).isoformat()},
        {'user_id': 'user2', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=1, hours=8)).isoformat()},
        {'user_id': 'user2', 'action_type': 'login', 'timestamp': (now - timedelta(hours=7)).isoformat()},
        {'user_id': 'user2', 'action_type': 'view_job', 'timestamp': (now - timedelta(hours=8)).isoformat()},
        
        {'user_id': 'user3', 'action_type': 'login', 'timestamp': (now - timedelta(days=1, hours=9)).isoformat()},
        {'user_id': 'user3', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=1, hours=10)).isoformat()},
        {'user_id': 'user3', 'action_type': 'login', 'timestamp': (now - timedelta(hours=9)).isoformat()},
        {'user_id': 'user3', 'action_type': 'view_job', 'timestamp': (now - timedelta(hours=10)).isoformat()}
    ]
    
    # Détecter les patterns
    detector.detect_patterns(user_actions)
    
    # Récupérer les patterns communs
    common_patterns = detector.get_common_patterns()
    
    # Vérifications
    assert 'common_time_periods' in common_patterns
    assert 'common_sequences' in common_patterns
    
    # Vérifier que 'login > view_job' est une séquence commune
    assert 'login > view_job' in common_patterns['common_sequences']