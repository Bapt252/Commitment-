from fastapi import APIRouter
from app.api.endpoints import users, jobs, companies, matching

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
