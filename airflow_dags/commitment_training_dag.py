from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
import json
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'commitment_model_training',
    default_args=default_args,
    description='Training pipeline for Commitment matching models',
    schedule_interval='0 0 * * 0',  # Hebdomadaire (dimanche à minuit)
)

def check_data_quality():
    """Vérifie la qualité des données avant l'entraînement"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import pandas as pd
    import os
    
    # Connexion à la base de données
    db_url = os.environ.get("DB_CONNECTION", "postgresql://user:password@localhost:5432/commitment")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Récupérer les feedbacks récents
        results = db.execute("SELECT * FROM matching_feedbacks ORDER BY feedback_date DESC LIMIT 1000").fetchall()
        if not results:
            return {"success": False, "issues": ["Aucun feedback trouvé"]}
        
        # Convertir en DataFrame
        feedbacks = pd.DataFrame(results)
        
        # Vérifications de base
        missing_values = feedbacks.isnull().sum().sum()
        rating_distribution = feedbacks['rating'].value_counts(normalize=True)
        
        # Détecter des anomalies
        has_issues = False
        issues = []
        
        if missing_values / (feedbacks.shape[0] * feedbacks.shape[1]) > 0.2:
            has_issues = True
            issues.append(f"Trop de valeurs manquantes: {missing_values}")
        
        if rating_distribution.get(5, 0) > 0.9:
            has_issues = True
            issues.append("Distribution de ratings suspecte (>90% de 5/5)")
        
        if feedbacks.shape[0] < 100:
            has_issues = True
            issues.append(f"Jeu de données trop petit: {feedbacks.shape[0]} entrées")
        
        if has_issues:
            return {
                'success': False,
                'issues': issues
            }
        else:
            return {
                'success': True
            }
    except Exception as e:
        logging.error(f"Erreur lors de la vérification des données: {str(e)}")
        return {'success': False, 'issues': [str(e)]}
    finally:
        db.close()

check_data_task = PythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    dag=dag,
)

# Trigger l'entraînement via l'API
train_model_task = SimpleHttpOperator(
    task_id='trigger_training',
    http_conn_id='commitment_api',
    endpoint='/api/feedback-system/train',
    method='POST',
    headers={"Content-Type": "application/json"},
    data=json.dumps({"force": True}),
    response_check=lambda response: response.json().get('success') == True,
    dag=dag,
)

# Vérifier les métriques du modèle entraîné
check_metrics_task = SimpleHttpOperator(
    task_id='check_metrics',
    http_conn_id='commitment_api',
    endpoint='/api/monitoring/models/matching',
    method='GET',
    response_check=lambda response: len(response.json()) > 0,
    dag=dag,
)

# Vérifier si le modèle est accessible après déploiement
check_deployment_task = HttpSensor(
    task_id='check_deployment',
    http_conn_id='commitment_api',
    endpoint='/api/monitoring/health',
    response_check=lambda response: response.json().get('models_status', {}).get('matching') == 'deployed',
    poke_interval=60,
    timeout=600,
    dag=dag,
)

# Déclenchement de la vérification des alertes
check_alerts_task = SimpleHttpOperator(
    task_id='check_alerts',
    http_conn_id='commitment_api',
    endpoint='/api/monitoring/check-alerts',
    method='POST',
    dag=dag,
)

check_data_task >> train_model_task >> check_metrics_task >> check_deployment_task >> check_alerts_task
