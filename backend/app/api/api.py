from fastapi import APIRouter
from app.api.endpoints import users, jobs, companies
from app.api.endpoints import job_posts, questionnaires, matching, feedback

api_router = APIRouter()

# Endpoints existants
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])

# Nouveaux endpoints pour l'API ML
api_router.include_router(job_posts.router, prefix="/job-posts", tags=["job-posts"])
api_router.include_router(questionnaires.router, prefix="/questionnaires", tags=["questionnaires"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
