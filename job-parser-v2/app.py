#!/usr/bin/env python3
"""
SuperSmartMatch V2 - Job Parser API Enrichie
============================================

API Python FastAPI avec extraction missions détaillées pour fiches de poste
- Parsing multi-formats (PDF, DOCX, TXT)
- NLP avancé (spaCy, NLTK)
- Enhanced mission parser intégré
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
import re
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

# NLP
import spacy
import nltk
from textblob import TextBlob

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/job-parser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("job-parser-v2")

# Métriques Prometheus
REQUESTS_TOTAL = Counter('job_parser_requests_total', 'Total job parsing requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('job_parser_request_duration_seconds', 'Request duration')
ACTIVE_REQUESTS = Gauge('job_parser_active_requests', 'Active requests')
MISSION_EXTRACTIONS = Counter('job_parser_missions_extracted_total', 'Total missions extracted')
CACHE_HITS = Counter('job_parser_cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('job_parser_cache_misses_total', 'Cache misses')

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

# Initialisation spaCy
try:
    nlp = spacy.load("fr_core_news_sm")
    logger.info("✅ spaCy French model loaded")
except Exception as e:
    logger.warning(f"⚠️ spaCy French model not found: {e}")
    nlp = None

# Initialisation FastAPI
app = FastAPI(
    title="SuperSmartMatch V2 - Job Parser",
    description="API enrichie pour parsing fiches de poste avec extraction missions détaillées",
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

class JobParserV2:
    """Parser fiche de poste enrichi avec extraction missions"""
    
    def __init__(self):
        self.version = PARSER_VERSION
        self.mission_extraction_enabled = MISSION_EXTRACTION
        
        # Patterns de reconnaissance pour jobs
        self.job_patterns = {
            'title': [
                r'(?:POSTE|OFFRE|EMPLOI|RECRUTEMENT)\s*:?\s*(.+)',
                r'RECHERCHE\s+(.+)',
                r'NOUS\s+RECRUTONS\s+(?:UN|UNE)?\s*(.+)',
                r'^(.+?)\s*(?:H/F|F/H|M/F)'
            ],
            'company': [
                r'(?:ENTREPRISE|SOCIÉTÉ|GROUPE|CABINET)\s*:?\s*(.+)',
                r'(?:CHEZ|AU SEIN DE|POUR)\s+(.+)',
                r'REJOIGNEZ\s+(.+)'
            ],
            'location': [
                r'(?:LIEU|LOCALISATION|RÉGION|VILLE)\s*:?\s*(.+)',
                r'(?:À|DANS|SUR)\s+([A-Z][a-z-]+(?:\s+[A-Z][a-z-]+)*)',
                r'(\d{5})\s+([A-Z][a-z-]+)'
            ],
            'contract': [
                r'(?:CONTRAT|TYPE)\s*:?\s*(.+)',
                r'(CDI|CDD|FREELANCE|STAGE|ALTERNANCE|INTÉRIM)',
                r'(?:EN|SOUS)\s+(CDI|CDD|FREELANCE|STAGE)'
            ],
            'salary': [
                r'(?:SALAIRE|RÉMUNÉRATION|PACKAGE)\s*:?\s*(.+)',
                r'(\d+(?:,\d+)?)\s*(?:€|euros?|K€)',
                r'ENTRE\s+(\d+(?:,\d+)?)\s*ET\s*(\d+(?:,\d+)?)\s*(?:€|K€)'
            ]
        }
        
    async def parse_job_with_missions(self, file_path: str, file_content: bytes = None) -> Dict[str, Any]:
        """Parse une fiche de poste avec extraction missions enrichies"""
        start_time = time.time()
        
        try:
            # Génération cache key
            cache_key = self._generate_cache_key(file_content or b'')
            
            # Vérification cache
            if redis_client:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    CACHE_HITS.inc()
                    logger.info(f"✅ Cache hit for Job: {cache_key[:8]}...")
                    return cached_result
                else:
                    CACHE_MISSES.inc()
            
            # Extraction texte du fichier
            text_content = await self._extract_text_from_file(file_path)
            
            # Parsing avec enhanced mission parser
            if self.mission_extraction_enabled:
                result = await self._parse_with_enhanced_parser(text_content, is_job=True)
            else:
                result = await self._parse_basic_job(text_content)
            
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
            if 'mission_analysis' in result:
                MISSION_EXTRACTIONS.inc(result['mission_analysis'].get('total_missions', 0))
            
            logger.info(f"✅ Job parsed successfully: {len(text_content)} chars, {time.time() - start_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Job parsing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Job parsing failed: {str(e)}")
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        """Extrait le texte d'un fichier (PDF, DOCX, TXT)"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return await self._extract_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                return await self._extract_from_docx(file_path)
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Format de fichier non supporté: {file_ext}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extraction PDF"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
    
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
    
    async def _parse_with_enhanced_parser(self, text: str, is_job: bool = True) -> Dict[str, Any]:
        """Utilise le parser Node.js enrichi pour jobs"""
        try:
            # Création fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(text)
                tmp_file_path = tmp_file.name
            
            # Appel du parser Node.js pour job
            cmd = ['node', '/app/enhanced-mission-parser.js', tmp_file_path, 'job']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Nettoyage
            os.unlink(tmp_file_path)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Enhanced parser failed: {result.stderr}")
                return await self._parse_basic_job(text)
                
        except subprocess.TimeoutExpired:
            logger.error("Enhanced parser timeout")
            return await self._parse_basic_job(text)
        except Exception as e:
            logger.error(f"Enhanced parser error: {e}")
            return await self._parse_basic_job(text)
    
    async def _parse_basic_job(self, text: str) -> Dict[str, Any]:
        """Parsing basique d'une fiche de poste"""
        result = {
            "title": self._extract_field(text, 'title'),
            "company": self._extract_field(text, 'company'),
            "location": self._extract_field(text, 'location'),
            "contract_type": self._extract_field(text, 'contract'),
            "salary": self._extract_field(text, 'salary'),
            "description": self._extract_description(text),
            "requirements": self._extract_requirements(text),
            "benefits": self._extract_benefits(text),
            "missions": self._extract_basic_missions(text),
            "parsing_confidence": 0.7,
            "raw_text": text[:500] + "..." if len(text) > 500 else text
        }
        
        # Analyse missions basique
        result['mission_analysis'] = {
            'total_missions': len(result['missions']),
            'by_category': self._categorize_basic_missions(result['missions']),
            'priority_missions': result['missions'][:3] if result['missions'] else []
        }
        
        return result
    
    def _extract_field(self, text: str, field_type: str) -> str:
        """Extrait un champ spécifique avec patterns regex"""
        patterns = self.job_patterns.get(field_type, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_description(self, text: str) -> str:
        """Extrait la description du poste"""
        # Recherche de sections description
        desc_patterns = [
            r'(?:DESCRIPTION|PRÉSENTATION|À PROPOS)\s*:?\s*(.*?)(?:\n\n|\n[A-Z])',
            r'(?:MISSIONS?|ACTIVITÉS?|RESPONSABILITÉS?)\s*:?\s*(.*?)(?:\n\n|\n[A-Z])',
            r'(?:VOUS|CANDIDAT)\s+(?:SEREZ|AUREZ)\s+(.*?)(?:\n\n|\n[A-Z])'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:500]  # Limite 500 chars
        
        # Fallback: premiers paragraphes
        lines = text.split('\n')
        description_lines = []
        for line in lines[3:8]:  # Skip header, take middle content
            if line.strip() and len(line) > 20:
                description_lines.append(line.strip())
        
        return ' '.join(description_lines)[:500]
    
    def _extract_requirements(self, text: str) -> Dict[str, Any]:
        """Extrait les prérequis et exigences"""
        requirements = {
            "experience": "",
            "education": "",
            "skills": [],
            "languages": []
        }
        
        # Expérience
        exp_match = re.search(r'(?:EXPÉRIENCE|EXPERIENCE)\s*:?\s*(.+?)(?:\n|\.)', text, re.IGNORECASE)
        if exp_match:
            requirements["experience"] = exp_match.group(1).strip()
        
        # Formation
        edu_match = re.search(r'(?:FORMATION|DIPLÔME|ÉTUDES)\s*:?\s*(.+?)(?:\n|\.)', text, re.IGNORECASE)
        if edu_match:
            requirements["education"] = edu_match.group(1).strip()
        
        # Compétences (patterns basiques)
        skill_patterns = [
            r'(?:MAÎTRISE|CONNAISSANCE)\s+(?:de|du|des|d\')\s+([^.\n]+)',
            r'(?:COMPÉTENCES?)\s*:?\s*([^.\n]+)',
            r'(?:SAVOIR-FAIRE)\s*:?\s*([^.\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                skills = [s.strip() for s in match.split(',')]
                requirements["skills"].extend(skills)
        
        return requirements
    
    def _extract_benefits(self, text: str) -> List[str]:
        """Extrait les avantages"""
        benefits = []
        
        benefit_patterns = [
            r'(?:AVANTAGES?|BÉNÉFICES?)\s*:?\s*([^.\n]+)',
            r'(?:NOUS OFFRONS|ON PROPOSE)\s+([^.\n]+)',
            r'(?:PACKAGE|RÉMUNÉRATION)\s+(?:COMPREND|INCLUT)\s+([^.\n]+)'
        ]
        
        for pattern in benefit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                benefit_items = [b.strip() for b in match.split(',')]
                benefits.extend(benefit_items)
        
        return benefits[:5]  # Limite 5 avantages
    
    def _extract_basic_missions(self, text: str) -> List[str]:
        """Extraction basique des missions"""
        missions = []
        
        # Recherche de listes à puces
        bullet_pattern = r'^\s*[•\-\*]\s+(.+)$'
        lines = text.split('\n')
        
        for line in lines:
            match = re.match(bullet_pattern, line)
            if match and len(match.group(1)) > 10:
                missions.append(match.group(1).strip())
        
        # Recherche de verbes d'action
        action_pattern = r'((?:Assurer|Effectuer|Gérer|Développer|Réaliser|Superviser|Coordonner|Analyser)[^.]+\.?)'
        action_matches = re.findall(action_pattern, text, re.IGNORECASE)
        missions.extend(action_matches)
        
        return missions[:10]  # Limite 10 missions
    
    def _categorize_basic_missions(self, missions: List[str]) -> Dict[str, int]:
        """Catégorisation basique des missions"""
        categories = {
            'gestion': 0,
            'technique': 0,
            'commercial': 0,
            'administratif': 0,
            'autres': 0
        }
        
        for mission in missions:
            mission_lower = mission.lower()
            if any(word in mission_lower for word in ['gérer', 'gestion', 'manager']):
                categories['gestion'] += 1
            elif any(word in mission_lower for word in ['technique', 'développer', 'analyser']):
                categories['technique'] += 1
            elif any(word in mission_lower for word in ['client', 'vente', 'commercial']):
                categories['commercial'] += 1
            elif any(word in mission_lower for word in ['administr', 'saisie', 'contrôle']):
                categories['administratif'] += 1
            else:
                categories['autres'] += 1
        
        return categories
    
    def _generate_cache_key(self, content: bytes) -> str:
        """Génère une clé de cache unique"""
        return hashlib.md5(content).hexdigest()
    
    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupère depuis le cache Redis"""
        try:
            cached = redis_client.get(f"job_parse:{key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None
    
    async def _save_to_cache(self, key: str, data: Dict[str, Any], ttl: int = 3600):
        """Sauvegarde en cache Redis"""
        try:
            redis_client.setex(f"job_parse:{key}", ttl, json.dumps(data))
        except Exception as e:
            logger.warning(f"Cache save error: {e}")

# Instance parser global
job_parser = JobParserV2()

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
            "nlp": "unknown"
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
    
    # Test NLP
    try:
        if nlp:
            doc = nlp("Test")
            health_status["services"]["nlp"] = "healthy"
    except:
        health_status["services"]["nlp"] = "unhealthy"
    
    return health_status

@app.post("/api/parse-job")
async def parse_job_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Endpoint principal pour parser une fiche de poste"""
    REQUESTS_TOTAL.labels(method="POST", endpoint="/api/parse-job").inc()
    
    # Validation fichier
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier requis")
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"Fichier trop volumineux (max: {MAX_FILE_SIZE//1024//1024}MB)")
    
    # Extensions supportées
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
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
        result = await job_parser.parse_job_with_missions(tmp_file_path, content)
        
        # Nettoyage en arrière-plan
        background_tasks.add_task(os.unlink, tmp_file_path)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse Job endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/api/stats")
async def get_stats():
    """Statistiques du parser"""
    REQUESTS_TOTAL.labels(method="GET", endpoint="/api/stats").inc()
    
    stats = {
        "version": PARSER_VERSION,
        "mission_extraction_enabled": MISSION_EXTRACTION,
        "cache_enabled": redis_client is not None,
        "nlp_enabled": nlp is not None,
        "supported_formats": [".pdf", ".docx", ".doc", ".txt"],
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
    logger.info(f"🚀 Starting SuperSmartMatch V2 - Job Parser {PARSER_VERSION}")
    logger.info(f"📊 Mission extraction: {'enabled' if MISSION_EXTRACTION else 'disabled'}")
    logger.info(f"🗄️ Redis cache: {'enabled' if redis_client else 'disabled'}")
    logger.info(f"🧠 NLP processing: {'enabled' if nlp else 'disabled'}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5053,
        reload=False,
        log_level=LOG_LEVEL,
        access_log=True
    )
