from fastapi import APIRouter

from app.api.endpoints import matching, feedback, jobs, job_posts, questionnaires, companies, users
from app.feedback_system import collector, monitoring

api_router = APIRouter()

# Routes API existantes
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(job_posts.router, prefix="/job-posts", tags=["job_posts"])
api_router.include_router(questionnaires.router, prefix="/questionnaires", tags=["questionnaires"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])

# Nouvelles routes pour le système d'amélioration continue
api_router.include_router(collector.router, prefix="/feedback-system", tags=["feedback_system"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
