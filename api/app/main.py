"""Point d'entrée principal de l'API Commitment."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routes.job_routes import router as job_router

app = FastAPI(
    title="Commitment API",
    description="API pour le parsing de fiches de poste et CV",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limitez aux origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajout des routes
app.include_router(job_router)

@app.get("/")
async def root():
    """Endpoint racine pour vérifier que l'API est en ligne."""
    return {
        "message": "Bienvenue sur l'API Commitment",
        "version": "1.0.0",
        "endpoints": {
            "jobs": {
                "parse": "/api/v1/jobs/parse",
                "parse_file": "/api/v1/jobs/parse-file"
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)