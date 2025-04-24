from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.experiment_manager import ExperimentManager
from app.services.metrics_collector import MetricsCollector
from app.database import db_session
from app.models.experiment import Experiment

experiments_bp = Blueprint('experiments', __name__)
experiment_manager = ExperimentManager(db_session)
metrics_collector = MetricsCollector(db_session)

@experiments_bp.route('/api/experiments', methods=['POST'])
@jwt_required()
def create_experiment():
    """Créer une nouvelle expérience"""
    try:
        data = request.get_json()
        experiment = experiment_manager.create_experiment(data)
        return jsonify({
            'id': experiment.id,
            'name': experiment.name,
            'status': experiment.status
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@experiments_bp.route('/api/experiments/<int:experiment_id>/start', methods=['POST'])
@jwt_required()
def start_experiment(experiment_id):
    """Démarrer une expérience"""
    experiment = db_session.query(Experiment).filter_by(id=experiment_id).first()
    if not experiment:
        return jsonify({'error': 'Experiment not found'}), 404
    
    if experiment.status != 'draft':
        return jsonify({'error': 'Experiment must be in draft status to start'}), 400
    
    experiment.status = 'running'
    db_session.commit()
    return jsonify({'status': 'success'})

@experiments_bp.route('/api/experiments/<int:experiment_id>/pause', methods=['POST'])
@jwt_required()
def pause_experiment(experiment_id):
    """Mettre en pause une expérience"""
    success = experiment_manager.pause_experiment(experiment_id)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Unable to pause experiment'}), 400

@experiments_bp.route('/api/experiments/<int:experiment_id>/metrics', methods=['GET'])
@jwt_required()
async def get_experiment_metrics(experiment_id):
    """Obtenir les métriques d'une expérience"""
    analysis = await metrics_collector.analyze_experiment(experiment_id)
    return jsonify(analysis)

@experiments_bp.route('/api/experiments', methods=['GET'])
@jwt_required()
def list_experiments():
    """Lister toutes les expériences"""
    experiments = db_session.query(Experiment).all()
    return jsonify([{
        'id': exp.id,
        'name': exp.name,
        'status': exp.status,
        'start_date': exp.start_date.isoformat(),
        'end_date': exp.end_date.isoformat() if exp.end_date else None
    } for exp in experiments])