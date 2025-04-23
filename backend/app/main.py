from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api.api import api_router

app = FastAPI(
    title="Commitment API",
    description="API pour la plateforme de matching Commitment",
    version="1.0.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limitez aux domaines réels
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajout des routes API
app.include_router(api_router, prefix="/api")

# Documentation personnalisée
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="Commitment API - Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
    )

@app.get("/api/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title="Commitment API",
        version="1.0.0",
        description="API pour la plateforme de matching Commitment",
        routes=app.routes,
    )

# Servir les fichiers statiques
app.mount("/", StaticFiles(directory="../", html=True), name="static")
