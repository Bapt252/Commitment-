# Ajouter cette importation en haut du fichier companies.py
from app.nlp.xgboost_matching import get_xgboost_matching_engine

# Ajouter ce nouvel endpoint après le endpoint match_candidates_for_company existant
@router.get("/match-xgboost/{company_id}/candidates", response_model=MatchingResponse)
async def match_candidates_xgboost(
    company_id: str,
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum de résultats"),
    min_score: float = Query(50.0, ge=0.0, le=100.0, description="Score minimal (%)"),
):
    """
    Génère des recommandations de candidats pour une entreprise spécifique
    en utilisant le modèle XGBoost pour un matching plus précis.
    """
    try:
        logger.info(f"Recherche de candidats avec XGBoost pour l'entreprise ID: {company_id}")
        
        # TODO: Remplacer par une vraie recherche en base de données
        # Ici, on simule des données pour la démonstration
        company_profile = {
            "id": company_id,
            "name": "Entreprise de démonstration",
            "extracted_data": {
                "values": {
                    "detected_values": {
                        "innovation": 0.8,
                        "collaboration": 0.7,
                        "autonomie": 0.6
                    }
                },
                "work_environment": {
                    "work_mode": ["hybrid"],
                    "locations": ["Paris"]
                },
                "experience": "3 ans"
            },
            "technologies": ["Python", "JavaScript", "AWS", "Docker"]
        }
        
        # Obtenir des candidats simulés
        # Dans une vraie implémentation, ces données viendraient d'une base de données
        candidate_profiles = [
            {
                "id": "c1",
                "name": "Jean Dupont",
                "titre": "Développeur Full Stack",
                "competences": ["Python", "JavaScript", "React", "Node.js"],
                "experience": [
                    {"period": "2020 - 2024", "title": "Développeur Full Stack chez TechCorp"}
                ],
                "values": {"detected_values": {"innovation": 0.9, "collaboration": 0.8}},
                "work_preferences": {"preferred_work_mode": "hybrid", "preferred_location": "Paris"}
            },
            {
                "id": "c2",
                "name": "Marie Martin",
                "titre": "DevOps Engineer",
                "competences": ["Docker", "AWS", "Python", "Kubernetes"],
                "experience": [
                    {"period": "2019 - 2024", "title": "DevOps Engineer chez CloudServices"}
                ],
                "values": {"detected_values": {"autonomie": 0.9, "excellence": 0.8}},
                "work_preferences": {"preferred_work_mode": "remote", "preferred_location": "Lyon"}
            }
            # Dans une implémentation réelle, il y aurait plus de candidats
        ]
        
        # Obtenir le moteur de matching XGBoost
        matching_engine = get_xgboost_matching_engine()
        
        # Générer les recommandations
        recommendations = matching_engine.generate_candidate_recommendations(
            company_profile, 
            candidate_profiles, 
            limit=limit
        )
        
        # Filtrer par score minimal
        filtered_recommendations = [r for r in recommendations if r["match_score"] >= min_score]
        
        # Construire la réponse
        response = {
            "results": filtered_recommendations,
            "count": len(filtered_recommendations),
            "company_id": company_id
        }
        
        return response
    except Exception as e:
        logger.error(f"Erreur lors du matching XGBoost: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching: {str(e)}"
        )