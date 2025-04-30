from fastapi import APIRouter

from app.api.endpoints import (
    chat, 
    companies, 
    cv_matcher, 
    cv_parser,  
    feedback, 
    geo,  # Nouveau module de géolocalisation
    job_posts, 
    matching, 
    parsing_chat,
    questionnaires, 
    users,
    health
)

api_router = APIRouter()

# Ajout des routes par module
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(cv_matcher.router, prefix="/cv-matcher", tags=["cv_matcher"])
api_router.include_router(cv_parser.router, prefix="/v1/cv", tags=["cv_parser"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(geo.router, prefix="/geo", tags=["geo"])  # Nouvelles routes de géolocalisation
api_router.include_router(job_posts.router, prefix="/job-posts", tags=["job_posts"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(parsing_chat.router, prefix="/parsing-chat", tags=["parsing_chat"])
api_router.include_router(questionnaires.router, prefix="/questionnaires", tags=["questionnaires"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
