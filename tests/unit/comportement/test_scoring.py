import pytest
from datetime import datetime, timedelta
from user_behavior.scoring.preference_calculator import PreferenceScoreCalculator


def test_calculate_preference_scores():
    # Test du calcul des scores de préférence
    calculator = PreferenceScoreCalculator()
    
    # Créer des données de test
    now = datetime.now()
    
    # Actions utilisateur simulées avec catégories
    user_actions = [
        {
            'user_id': 'user1',
            'action_type': 'view_job',
            'timestamp': (now - timedelta(days=1)).isoformat(),
            'item_id': 'job1',
            'job_category': 'Development'
        },
        {
            'user_id': 'user1',
            'action_type': 'apply_job',
            'timestamp': now.isoformat(),
            'item_id': 'job1',
            'job_category': 'Development'
        },
        {
            'user_id': 'user1',
            'action_type': 'view_job',
            'timestamp': (now - timedelta(days=2)).isoformat(),
            'item_id': 'job2',
            'job_category': 'Data Science'
        },
        {
            'user_id': 'user2',
            'action_type': 'view_job',
            'timestamp': (now - timedelta(days=1)).isoformat(),
            'item_id': 'job3',
            'job_category': 'Management'
        },
        {
            'user_id': 'user2',
            'action_type': 'view_job',
            'timestamp': now.isoformat(),
            'item_id': 'job4',
            'job_category': 'Management'
        }
    ]
    
    # Calculer les scores
    scores = calculator.calculate_preference_scores(user_actions, now=now)
    
    # Vérifications
    assert len(scores) == 2
    assert 'user1' in scores
    assert 'user2' in scores
    
    # Vérifier les scores pour user1
    user1_scores = scores['user1']
    assert 'Development' in user1_scores
    assert 'Data Science' in user1_scores
    
    # Development devrait avoir un score plus élevé (vue + candidature + plus récent)
    assert user1_scores['Development'] > user1_scores['Data Science']
    
    # La somme des scores devrait être égale à 1 (normalisation)
    assert abs(sum(user1_scores.values()) - 1.0) < 0.001
    
    # Vérifier les scores pour user2
    user2_scores = scores['user2']
    assert 'Management' in user2_scores
    assert user2_scores['Management'] == 1.0  # Une seule catégorie


def test_update_preference_scores():
    # Test de la mise à jour des scores de préférence
    calculator = PreferenceScoreCalculator()
    
    # Créer des données de test
    now = datetime.now()
    
    # Scores existants
    existing_scores = {
        'user1': {
            'Development': 0.7,
            'Data Science': 0.3
        }
    }
    
    # Nouvelles actions
    new_actions = [
        {
            'user_id': 'user1',
            'action_type': 'view_job',
            'timestamp': now.isoformat(),
            'item_id': 'job5',
            'job_category': 'DevOps'
        },
        {
            'user_id': 'user2',
            'action_type': 'view_job',
            'timestamp': now.isoformat(),
            'item_id': 'job6',
            'job_category': 'Management'
        }
    ]
    
    # Mettre à jour les scores
    updated_scores = calculator.update_preference_scores(existing_scores, new_actions, now=now)
    
    # Vérifications
    assert len(updated_scores) == 2
    assert 'user1' in updated_scores
    assert 'user2' in updated_scores
    
    # Vérifier la mise à jour des scores pour user1
    user1_scores = updated_scores['user1']
    assert 'Development' in user1_scores
    assert 'Data Science' in user1_scores
    assert 'DevOps' in user1_scores  # Nouvelle catégorie
    
    # La somme des scores devrait être égale à 1 (normalisation)
    assert abs(sum(user1_scores.values()) - 1.0) < 0.001