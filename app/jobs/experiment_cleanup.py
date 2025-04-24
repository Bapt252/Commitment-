from datetime import datetime
from app.database import db_session
from app.models.experiment import Experiment

def cleanup_expired_experiments():
    """Nettoyer les expériences expirées"""
    now = datetime.utcnow()
    expired_experiments = db_session.query(Experiment).filter(
        Experiment.status == 'running',
        Experiment.end_date < now
    ).all()
    
    for experiment in expired_experiments:
        experiment.status = 'completed'
    
    db_session.commit()
    print(f"Cleaned up {len(expired_experiments)} expired experiments")

# À ajouter à votre Redis Queue scheduler
# Exemple:
# from rq import Queue
# from redis import Redis
# queue = Queue(connection=Redis())
# queue.enqueue(cleanup_expired_experiments)