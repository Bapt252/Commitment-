#!/usr/bin/env python3
"""
SuperSmartMatch V2 - CV Parser API Enrichie
==========================================

API Python FastAPI avec extraction missions détaillées
- Parsing multi-formats (PDF, DOCX, images)
- OCR intégré (Tesseract)
- Enhanced mission parser
- Cache Redis optimisé
- Monitoring Prometheus

Version: 2.0.0
Author: Baptiste Coma
Created: June 2025
"""

import os
import sys
import json
import subprocess
import tempfile
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# FastAPI et web
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

# Processing
import redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import hashlib

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/cv-parser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cv-parser-v2")

# Métriques Prometheus
REQUESTS_TOTAL = Counter('cv_parser_requests_total', 'Total CV parsing requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('cv_parser_request_duration_seconds', 'Request duration')
ACTIVE_REQUESTS = Gauge('cv_parser_active_requests', 'Active requests')
MISSION_EXTRACTIONS = Counter('cv_parser_missions_extracted_total', 'Total missions extracted')
CACHE_HITS = Counter('cv_parser_cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('cv_parser_cache_misses_total', 'Cache misses')

# Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')
PARSER_VERSION = os.getenv('PARSER_VERSION', '2.0.0')
MISSION_EXTRACTION = os.getenv('MISSION_EXTRACTION', 'enabled') == 'enabled'
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10')) * 1024 * 1024  # 10MB par défaut

# Initialisation Redis
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis connection established")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    redis_client = None

# Initialisation FastAPI
app = FastAPI(
    title="SuperSmartMatch V2 - CV Parser",
    description="API enrichie pour parsing CV avec extraction missions détaillées",
    version=PARSER_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

class CVParserV2:
    """Parser CV enrichi avec extraction missions"""
    
    def __init__(self):
        self.version = PARSER_VERSION
        self.mission_extraction_enabled = MISSION_EXTRACTION
        
    async def parse_cv_with_missions(self, file_path: str, file_content: bytes = None) -> Dict[str, Any]:
        """Parse un CV avec extraction missions enrichies"""
        start_time = time.time()
        
        try:
            # Génération cache key
            cache_key = self._generate_cache_key(file_content or b'')
            
            # Vérification cache
            if redis_client:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    CACHE_HITS.inc()
                    logger.info(f"✅ Cache hit for CV: {cache_key[:8]}...")
                    return cached_result
                else:
                    CACHE_MISSES.inc()
            
            # Extraction texte du fichier
            text_content = await self._extract_text_from_file(file_path)
            
            # Parsing avec enhanced mission parser
            if self.mission_extraction_enabled:
                result = await self._parse_with_enhanced_parser(text_content)
            else:
                result = await self._parse_basic(text_content)
            
            # Enrichissement avec métadonnées
            result['parsing_metadata'] = {
                'version': self.version,
                'timestamp': datetime.utcnow().isoformat(),
                'processing_time': round(time.time() - start_time, 3),
                'mission_extraction_enabled': self.mission_extraction_enabled,
                'cache_key': cache_key
            }
            
            # Mise en cache
            if redis_client:
                await self._save_to_cache(cache_key, result)
            
            # Métriques
            if 'mission_summary' in result:
                MISSION_EXTRACTIONS.inc(result['mission_summary'].get('total_missions', 0))
            
            logger.info(f"✅ CV parsed successfully: {len(text_content)} chars, {time.time() - start_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ CV parsing failed: {e}")
            raise HTTPException(status_code=500, detail=f"CV parsing failed: {str(e)}")
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        """Extrait le texte d'un fichier (PDF, DOCX, image)"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return await self._extract_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                return await self._extract_from_docx(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                return await self._extract_from_image(file_path)
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Format de fichier non supporté: {file_ext}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extraction PDF avec fallback OCR"""
        try:
            # Tentative avec pdfplumber (rapide)
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Si peu de texte, utiliser OCR
            if len(text.strip()) < 100:
                logger.info("PDF text extraction insufficient, using OCR")
                text = await self._extract_with_ocr(file_path)
            
            return text
            
        except Exception as e:
            logger.warning(f"PDF extraction failed, trying OCR: {e}")
            return await self._extract_with_ocr(file_path)
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extraction DOCX"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise
    
    async def _extract_from_image(self, file_path: str) -> str:
        """Extraction image avec OCR"""
        return await self._extract_with_ocr(file_path)
    
    async def _extract_with_ocr(self, file_path: str) -> str:
        """Extraction OCR avec Tesseract"""
        try:
            import pytesseract
            from PIL import Image
            
            # Si PDF, convertir en images d'abord
            if file_path.endswith('.pdf'):
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img, lang='fra+eng')
                    text += page_text + "\n"
                doc.close()
                return text
            else:
                # Image directe
                img = Image.open(file_path)
                return pytesseract.image_to_string(img, lang='fra+eng')
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
    
    async def _parse_with_enhanced_parser(self, text: str) -> Dict[str, Any]:
        """Utilise le parser Node.js enrichi"""
        try:
            # Création fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(text)
                tmp_file_path = tmp_file.name
            
            # Appel du parser Node.js
            cmd = ['node', '/app/enhanced-mission-parser.js', tmp_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Nettoyage
            os.unlink(tmp_file_path)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Enhanced parser failed: {result.stderr}")
                return await self._parse_basic(text)
                
        except subprocess.TimeoutExpired:
            logger.error("Enhanced parser timeout")
            return await self._parse_basic(text)
        except Exception as e:
            logger.error(f"Enhanced parser error: {e}")
            return await self._parse_basic(text)
    
    async def _parse_basic(self, text: str) -> Dict[str, Any]:
        """Parsing basique sans missions enrichies"""
        return {
            "personal_info": {},
            "professional_experience": [],
            "education": [],
            "skills": [],
            "languages": [],
            "parsing_confidence": 0.7,
            "raw_text": text[:500] + "..." if len(text) > 500 else text
        }
    
    def _generate_cache_key(self, content: bytes) -> str:
        """Génère une clé de cache unique"""
        return hashlib.md5(content).hexdigest()
    
    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupère depuis le cache Redis"""
        try:
            cached = redis_client.get(f"cv_parse:{key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None
    
    async def _save_to_cache(self, key: str, data: Dict[str, Any], ttl: int = 3600):
        """Sauvegarde en cache Redis"""
        try:
            redis_client.setex(f"cv_parse:{key}", ttl, json.dumps(data))
        except Exception as e:
            logger.warning(f"Cache save error: {e}")

# Instance parser global
cv_parser = CVParserV2()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware pour mesurer le temps de traitement"""
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        REQUEST_DURATION.observe(process_time)
        return response
    finally:
        ACTIVE_REQUESTS.dec()

@app.get("/")
async def root():
    """Page d'accueil avec redirection vers docs"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    REQUESTS_TOTAL.labels(method="GET", endpoint="/health").inc()
    
    # Tests de santé
    health_status = {
        "status": "healthy",
        "version": PARSER_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "redis": "unknown",
            "enhanced_parser": "unknown",
            "ocr": "unknown"
        }
    }
    
    # Test Redis
    try:
        if redis_client:
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
    except:
        health_status["services"]["redis"] = "unhealthy"
    
    # Test Enhanced Parser
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            health_status["services"]["enhanced_parser"] = "healthy"
    except:
        health_status["services"]["enhanced_parser"] = "unhealthy"
    
    # Test OCR
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        health_status["services"]["ocr"] = "healthy"
    except:
        health_status["services"]["ocr"] = "unhealthy"
    
    return health_status

@app.post("/api/parse-cv/")
async def parse_cv_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Endpoint principal pour parser un CV"""
    REQUESTS_TOTAL.labels(method="POST", endpoint="/api/parse-cv/").inc()
    
    # Validation fichier
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier requis")
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"Fichier trop volumineux (max: {MAX_FILE_SIZE//1024//1024}MB)")
    
    # Extensions supportées
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png', '.bmp'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Extension non supportée: {file_ext}")
    
    # Sauvegarde temporaire
    try:
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Parsing
        result = await cv_parser.parse_cv_with_missions(tmp_file_path, content)
        
        # Nettoyage en arrière-plan
        background_tasks.add_task(os.unlink, tmp_file_path)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse CV endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/api/stats")
async def get_stats():
    """Statistiques du parser"""
    REQUESTS_TOTAL.labels(method="GET", endpoint="/api/stats").inc()
    
    stats = {
        "version": PARSER_VERSION,
        "mission_extraction_enabled": MISSION_EXTRACTION,
        "cache_enabled": redis_client is not None,
        "supported_formats": [".pdf", ".docx", ".doc", ".txt", ".jpg", ".jpeg", ".png", ".bmp"],
        "max_file_size_mb": MAX_FILE_SIZE // 1024 // 1024
    }
    
    if redis_client:
        try:
            info = redis_client.info()
            stats["cache_info"] = {
                "used_memory": info.get('used_memory_human'),
                "connected_clients": info.get('connected_clients'),
                "total_commands_processed": info.get('total_commands_processed')
            }
        except:
            pass
    
    return stats

@app.get("/metrics")
async def metrics():
    """Métriques Prometheus"""
    return generate_latest()

@app.get("/api/cache/clear")
async def clear_cache():
    """Vide le cache (dev uniquement)"""
    if redis_client:
        try:
            redis_client.flushdb()
            return {"message": "Cache cleared successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cache clear failed: {e}")
    else:
        raise HTTPException(status_code=503, detail="Cache not available")

if __name__ == "__main__":
    logger.info(f"🚀 Starting SuperSmartMatch V2 - CV Parser {PARSER_VERSION}")
    logger.info(f"📊 Mission extraction: {'enabled' if MISSION_EXTRACTION else 'disabled'}")
    logger.info(f"🗄️ Redis cache: {'enabled' if redis_client else 'disabled'}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5051,
        reload=False,
        log_level=LOG_LEVEL,
        access_log=True
    )
