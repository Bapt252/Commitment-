import pytest
from user_behavior.clustering.kmeans_clustering import UserClusterer


def test_prepare_data():
    # Test de la préparation des données pour le clustering
    clusterer = UserClusterer()
    
    # Données de test
    user_profiles = [
        {
            'user_id': 'user1',
            'session_count': 10,
            'avg_session_duration': 5,
            'job_view_count': 20,
            'application_count': 2,
            'profile_completion': 80,
            'recency_score': 0.9,
            'engagement_score': 0.7
        },
        {
            'user_id': 'user2',
            'session_count': 5,
            'avg_session_duration': 3,
            'job_view_count': 10,
            'application_count': 1,
            'profile_completion': 50,
            'recency_score': 0.5,
            'engagement_score': 0.3
        }
    ]
    
    df, user_ids = clusterer.prepare_data(user_profiles)
    
    # Vérifications
    assert len(df) == 2
    assert len(user_ids) == 2
    assert user_ids == ['user1', 'user2']
    assert list(df.columns) == [
        'session_count', 'avg_session_duration', 'job_view_count',
        'application_count', 'profile_completion', 'recency_score',
        'engagement_score'
    ]


def test_fit_predict():
    # Test d'entraînement et de prédiction du modèle
    clusterer = UserClusterer(n_clusters=2)
    
    # Données de test
    user_profiles = [
        {
            'user_id': 'user1',
            'session_count': 10,
            'avg_session_duration': 5,
            'job_view_count': 20,
            'application_count': 2,
            'profile_completion': 80,
            'recency_score': 0.9,
            'engagement_score': 0.7
        },
        {
            'user_id': 'user2',
            'session_count': 5,
            'avg_session_duration': 3,
            'job_view_count': 10,
            'application_count': 1,
            'profile_completion': 50,
            'recency_score': 0.5,
            'engagement_score': 0.3
        },
        {
            'user_id': 'user3',
            'session_count': 8,
            'avg_session_duration': 4,
            'job_view_count': 15,
            'application_count': 1,
            'profile_completion': 70,
            'recency_score': 0.7,
            'engagement_score': 0.5
        },
        {
            'user_id': 'user4',
            'session_count': 3,
            'avg_session_duration': 2,
            'job_view_count': 5,
            'application_count': 0,
            'profile_completion': 30,
            'recency_score': 0.3,
            'engagement_score': 0.1
        }
    ]
    
    # Entraînement
    clusterer.fit(user_profiles)
    
    # Vérification de l'entraînement
    assert clusterer.fitted
    assert clusterer.model.n_clusters == 2
    assert clusterer.cluster_centers.shape == (2, 7)
    
    # Prédiction
    assignments = clusterer.predict(user_profiles)
    
    # Vérification des prédictions
    assert len(assignments) == 4
    assert all(label in [0, 1] for label in assignments.values())
    
    # Les utilisateurs similaires devraient être dans le même cluster
    assert assignments['user1'] == assignments['user3'] or assignments['user2'] == assignments['user4']


def test_get_cluster_profiles():
    # Test de la génération des profils de cluster
    clusterer = UserClusterer(n_clusters=2)
    
    # Données de test (identiques au test précédent)
    user_profiles = [
        {
            'user_id': 'user1',
            'session_count': 10,
            'avg_session_duration': 5,
            'job_view_count': 20,
            'application_count': 2,
            'profile_completion': 80,
            'recency_score': 0.9,
            'engagement_score': 0.7
        },
        {
            'user_id': 'user2',
            'session_count': 5,
            'avg_session_duration': 3,
            'job_view_count': 10,
            'application_count': 1,
            'profile_completion': 50,
            'recency_score': 0.5,
            'engagement_score': 0.3
        },
        {
            'user_id': 'user3',
            'session_count': 8,
            'avg_session_duration': 4,
            'job_view_count': 15,
            'application_count': 1,
            'profile_completion': 70,
            'recency_score': 0.7,
            'engagement_score': 0.5
        },
        {
            'user_id': 'user4',
            'session_count': 3,
            'avg_session_duration': 2,
            'job_view_count': 5,
            'application_count': 0,
            'profile_completion': 30,
            'recency_score': 0.3,
            'engagement_score': 0.1
        }
    ]
    
    # Entraînement
    clusterer.fit(user_profiles)
    
    # Génération des profils de cluster
    cluster_profiles = clusterer.get_cluster_profiles()
    
    # Vérifications
    assert len(cluster_profiles) == 2
    assert all('cluster_id' in profile for profile in cluster_profiles)
    assert all('center' in profile for profile in cluster_profiles)
    assert all('description' in profile for profile in cluster_profiles)