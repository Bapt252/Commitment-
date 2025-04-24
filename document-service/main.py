import uuid
import hashlib
import io
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query, Path, Request, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from loguru import logger
import redis

# Import des modules locaux
from config import settings
from database import get_db, init_db, check_db_connection
from models import Document, DocumentPermission, DocumentAccessLog, PresignedUrl
from schemas import (
    DocumentCreate, DocumentResponse, DocumentDetailResponse, DocumentListResponse,
    PermissionCreate, PermissionResponse, AccessLogResponse, 
    PresignedUrlCreate, PresignedUrlResponse, 
    DocumentBatchProcessRequest, DocumentBatchProcessResponse
)
from auth import (
    get_current_user, check_document_permission, log_access_attempt,
    get_accessible_documents, oauth2_scheme
)
from storage import storage_client
from security import SecurityUtils
from expiration import calculate_expiry_date

# Configuration du logger
logger.add(
    "logs/api.log",
    rotation="10 MB",
    level=settings.LOG_LEVEL,
    format="{time} {level} {message}",
    serialize=settings.LOG_FORMAT == "json"
)

# Initialisation de l'application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À adapter en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion Redis
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


# Événements au démarrage et à l'arrêt
@app.on_event("startup")
async def startup_event():
    """
    Événement exécuté au démarrage de l'application
    """
    logger.info(f"Démarrage de l'API Document Service v{settings.APP_VERSION}")
    
    # Vérifier la connexion à la base de données
    if not check_db_connection():
        logger.error("Impossible de se connecter à la base de données")
        raise Exception("Database connection failed")
    
    # Initialiser la base de données si nécessaire
    init_db()
    
    # Vérifier la connexion à Redis
    try:
        redis_conn.ping()
        logger.info("Connexion Redis établie")
    except Exception as e:
        logger.error(f"Erreur de connexion Redis: {str(e)}")
        raise
    
    # Vérifier l'accès à MinIO
    try:
        storage_client._ensure_buckets_exist()
        logger.info("Connexion MinIO établie")
    except Exception as e:
        logger.error(f"Erreur de connexion MinIO: {str(e)}")
        raise


@app.on_event("shutdown")
def shutdown_event():
    """
    Événement exécuté à l'arrêt de l'application
    """
    logger.info("Arrêt de l'API Document Service")


# Routes de santé et de statut
@app.get("/health", include_in_schema=False)
async def health_check():
    """
    Endpoint de vérification de santé pour monitoring
    """
    db_ok = check_db_connection()
    redis_ok = False
    minio_ok = False
    
    try:
        redis_ok = redis_conn.ping()
    except:
        pass
    
    try:
        minio_ok = storage_client.check_file_exists("health_check.txt")
    except:
        pass
    
    status = all([db_ok, redis_ok, minio_ok])
    
    return {
        "status": "healthy" if status else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "services": {
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
            "storage": "connected" if minio_ok else "disconnected"
        }
    }


@app.get("/status", include_in_schema=False)
async def service_status(current_user: dict = Depends(get_current_user)):
    """
    Endpoint de statut détaillé pour les administrateurs
    """
    # Statistiques de base
    db = next(get_db())
    total_documents = db.query(func.count(Document.id)).scalar()
    active_documents = db.query(func.count(Document.id)).filter(Document.status == "active").scalar()
    
    # Statistiques par type de document
    doc_types = db.query(
        Document.document_type, 
        func.count(Document.id)
    ).group_by(Document.document_type).all()
    
    doc_type_stats = {doc_type: count for doc_type, count in doc_types}
    
    # Statistiques sur les expirations
    expiring_soon = db.query(func.count(Document.id)).filter(
        Document.expires_at.between(
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=30)
        ),
        Document.status == "active"
    ).scalar()
    
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "statistics": {
            "total_documents": total_documents,
            "active_documents": active_documents,
            "document_types": doc_type_stats,
            "expiring_soon": expiring_soon
        }
    }


# Routes principales pour les documents
@app.post("/documents/", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Type de document (cv, cover_letter, job_description)"),
    metadata: Optional[Dict[str, Any]] = None,
    expires_in_days: Optional[int] = Query(365, gt=0, lt=3650),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Télécharge un nouveau document et l'enregistre dans le système
    """
    # Validation du type de document
    if document_type not in settings.ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type de document non valide. Types autorisés: {', '.join(settings.ALLOWED_DOCUMENT_TYPES)}"
        )
    
    # Validation du type MIME
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non autorisé. Types autorisés: {', '.join(settings.ALLOWED_MIME_TYPES)}"
        )
    
    # Génération d'un ID unique pour le document
    document_id = uuid.uuid4()
    
    try:
        # Lecture du contenu pour vérification
        content = await file.read()
        file_size = len(content)
        
        # Vérification de la taille
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Fichier trop volumineux. Taille maximale: {settings.MAX_UPLOAD_SIZE} octets"
            )
        
        # Calcul du hash pour vérification d'intégrité
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Génération d'un nom de fichier sécurisé et unique
        safe_filename = SecurityUtils.sanitize_filename(file.filename)
        object_key = f"{document_type}/{document_id}/{safe_filename}"
        
        # Réinitialiser le curseur du fichier
        await file.seek(0)
        
        # Téléchargement vers MinIO
        upload_result = await storage_client.upload_file(
            file=file,
            object_key=object_key,
            bucket_name=settings.DOCUMENT_BUCKET
        )
        
        # Calcul de la date d'expiration
        expires_at = calculate_expiry_date(expires_in_days)
        
        # Création de l'enregistrement dans la base de données
        new_document = Document(
            id=document_id,
            filename=safe_filename,
            original_filename=file.filename,
            mime_type=file.content_type,
            size_bytes=file_size,
            bucket_name=settings.DOCUMENT_BUCKET,
            object_key=object_key,
            content_hash=content_hash,
            status="pending",  # En attente de validation par l'antivirus
            document_type=document_type,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        # Ajouter permission de base pour l'uploader
        new_permission = DocumentPermission(
            document_id=document_id,
            entity_type="user",
            entity_id=current_user["id"],
            permission_type="admin",  # Contrôle total pour l'uploader
            granted_by=current_user["id"]
        )
        db.add(new_permission)
        db.commit()
        
        # Envoyer le fichier à la file d'attente pour analyse antivirus
        from rq import Queue
        security_queue = Queue('document_security', connection=redis_conn)
        
        job = security_queue.enqueue(
            'security_scan_job',
            document_id=str(document_id),
            object_key=object_key,
            bucket_name=settings.DOCUMENT_BUCKET,
            job_timeout=settings.REDIS_JOB_TIMEOUT,
            result_ttl=3600
        )
        
        logger.info(f"Document {document_id} téléchargé et envoyé pour analyse de sécurité (job: {job.id})")
        
        return DocumentResponse.model_validate(new_document)
    
    except HTTPException:
        # Re-lever les exceptions HTTP déjà générées
        raise
    
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement du document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du téléchargement du document"
        )


@app.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: uuid.UUID = Path(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Récupère les métadonnées d'un document spécifique
    """
    # Récupérer le document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier les permissions
    has_permission = check_document_permission(db, document_id, current_user["id"], "read")
    if not has_permission:
        # Logger la tentative d'accès non autorisée
        log_access_attempt(db, document_id, current_user["id"], "view", False, request)
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Logger l'accès autorisé
    log_access_attempt(db, document_id, current_user["id"], "view", True, request)
    
    return DocumentDetailResponse.model_validate(document)


@app.get("/documents/{document_id}/access", response_model=PresignedUrlResponse)
async def get_document_access(
    background_tasks: BackgroundTasks,
    document_id: uuid.UUID = Path(...),
    expires_in_seconds: int = Query(300, gt=0, lt=86400),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Génère une URL pré-signée pour accéder au document
    """
    # Récupérer le document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document or document.status not in ["active", "pending"]:
        raise HTTPException(status_code=404, detail="Document non trouvé ou non disponible")
    
    # Vérifier les permissions
    has_permission = check_document_permission(db, document_id, current_user["id"], "read")
    if not has_permission:
        log_access_attempt(db, document_id, current_user["id"], "download", False, request)
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Générer l'URL pré-signée
    url = storage_client.generate_presigned_url(
        object_key=document.object_key,
        expires_in_seconds=expires_in_seconds,
        bucket_name=document.bucket_name
    )
    
    # Enregistrer l'URL pré-signée pour audit
    expiry_datetime = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
    presigned_url = PresignedUrl(
        document_id=document_id,
        url=url,
        expires_at=expiry_datetime,
        created_by=current_user["id"]
    )
    db.add(presigned_url)
    db.commit()
    
    # Logger l'accès
    log_access_attempt(db, document_id, current_user["id"], "download", True, request)
    
    # Envoyer une notification asynchrone au propriétaire du document (si ce n'est pas lui-même)
    if document.id != current_user["id"]:
        from rq import Queue
        notification_queue = Queue('document_notification', connection=redis_conn)
        
        background_tasks.add_task(
            lambda: notification_queue.enqueue(
                'send_download_notification',
                document_id=str(document_id),
                downloader_id=str(current_user["id"])
            )
        )
    
    return PresignedUrlResponse(
        id=presigned_url.id,
        document_id=document_id,
        url=url,
        expires_at=expiry_datetime
    )


@app.get("/documents/{document_id}/content")
async def get_document_content(
    document_id: uuid.UUID = Path(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Récupère directement le contenu d'un document (streaming)
    """
    # Récupérer le document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document or document.status not in ["active", "pending"]:
        raise HTTPException(status_code=404, detail="Document non trouvé ou non disponible")
    
    # Vérifier les permissions
    has_permission = check_document_permission(db, document_id, current_user["id"], "read")
    if not has_permission:
        log_access_attempt(db, document_id, current_user["id"], "download", False, request)
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Logger l'accès
    log_access_attempt(db, document_id, current_user["id"], "download", True, request)
    
    try:
        # Récupérer le contenu depuis MinIO
        response = storage_client.download_file(
            object_key=document.object_key,
            bucket_name=document.bucket_name
        )
        
        # Créer une fonction de streaming pour le contenu
        def iterfile():
            try:
                for data in response.stream(32*1024):
                    yield data
            finally:
                response.close()
                response.release_conn()
        
        return StreamingResponse(
            iterfile(),
            media_type=document.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{document.filename}\""
            }
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération du contenu du document"
        )


@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: uuid.UUID = Path(...),
    permanent: bool = Query(False, description="Suppression permanente (true) ou mise en corbeille (false)"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Supprime un document (corbeille ou définitivement)
    """
    # Récupérer le document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier les permissions
    has_permission = check_document_permission(db, document_id, current_user["id"], "delete")
    if not has_permission:
        log_access_attempt(db, document_id, current_user["id"], "delete", False, request)
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    try:
        if permanent:
            # Suppression physique du fichier
            storage_client.delete_file(
                object_key=document.object_key,
                bucket_name=document.bucket_name
            )
            
            # Suppression de la base de données
            db.delete(document)
        else:
            # Mise en corbeille (soft delete)
            document.status = "deleted"
            document.updated_at = datetime.utcnow()
            document.metadata = {
                **(document.metadata or {}),
                "deleted_at": datetime.utcnow().isoformat(),
                "deleted_by": str(current_user["id"])
            }
        
        db.commit()
        
        # Logger la suppression
        log_access_attempt(db, document_id, current_user["id"], "delete", True, request)
        
        return {"status": "success", "message": "Document supprimé avec succès"}
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression du document"
        )


@app.put("/documents/{document_id}/restore")
async def restore_document(
    document_id: uuid.UUID = Path(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Restaure un document supprimé (depuis la corbeille)
    """
    # Récupérer le document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.status == "deleted"
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document supprimé non trouvé")
    
    # Vérifier les permissions
    has_permission = check_document_permission(db, document_id, current_user["id"], "admin")
    if not has_permission:
        log_access_attempt(db, document_id, current_user["id"], "restore", False, request)
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    try:
        # Restaurer le document
        document.status = "active"
        document.updated_at = datetime.utcnow()
        
        # Mettre à jour les métadonnées
        metadata = document.metadata or {}
        metadata["restored_at"] = datetime.utcnow().isoformat()
        metadata["restored_by"] = str(current_user["id"])
        document.metadata = metadata
        
        db.commit()
        
        # Logger la restauration
        log_access_attempt(db, document_id, current_user["id"], "restore", True, request)
        
        return {"status": "success", "message": "Document restauré avec succès"}
    
    except Exception as e:
        logger.error(f"Erreur lors de la restauration du document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la restauration du document"
        )


@app.get("/documents/", response_model=DocumentListResponse)
async def list_documents(
    document_type: Optional[str] = Query(None, description="Filtrer par type de document"),
    status: Optional[str] = Query("active", description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche dans le nom ou les métadonnées"),
    page: int = Query(1, gt=0, description="Numéro de page"),
    limit: int = Query(20, gt=0, lt=100, description="Nombre d'éléments par page"),
    sort_by: Optional[str] = Query("created_at", description="Champ de tri"),
    sort_order: Optional[str] = Query("desc", description="Ordre de tri (asc, desc)"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Liste les documents accessibles par l'utilisateur courant avec pagination et filtrage
    """
    # Construction de la requête
    query = db.query(Document)
    
    # Filtres
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if status:
        query = query.filter(Document.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Document.filename.ilike(search_term),
                Document.original_filename.ilike(search_term)
                # Note: la recherche dans les métadonnées JSON demanderait plus de code spécifique à PostgreSQL
            )
        )
    
    # Filtrer par permissions de l'utilisateur
    accessible_documents = get_accessible_documents(db, current_user["id"])
    query = query.filter(Document.id.in_(accessible_documents))
    
    # Compter le total avant pagination
    total = query.count()
    
    # Appliquer le tri
    sort_column = getattr(Document, sort_by, Document.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Appliquer la pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    # Calculer le nombre total de pages
    total_pages = (total + limit - 1) // limit
    
    # Exécuter la requête
    documents = query.all()
    
    return {
        "items": documents,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": total_pages
    }


@app.post("/documents/batch", response_model=DocumentBatchProcessResponse)
async def batch_process_documents(
    batch_request: DocumentBatchProcessRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Traitement par lot de documents (archivage, suppression, extension de durée...)
    """
    successful_ids = []
    failed_ids = []
    
    for doc_id in batch_request.document_ids:
        try:
            # Vérifier l'existence du document
            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                failed_ids.append(doc_id)
                continue
            
            # Vérifier les permissions selon l'opération
            permission_type = "admin"
            if batch_request.operation == "delete":
                permission_type = "delete"
            
            has_permission = check_document_permission(db, doc_id, current_user["id"], permission_type)
            if not has_permission:
                failed_ids.append(doc_id)
                continue
            
            # Effectuer l'opération demandée
            if batch_request.operation == "archive":
                # Archiver le document
                storage_client.archive_file(
                    object_key=document.object_key,
                    source_bucket=document.bucket_name,
                    target_bucket=settings.ARCHIVE_BUCKET
                )
                
                document.status = "archived"
                document.updated_at = datetime.utcnow()
                document.metadata = {
                    **(document.metadata or {}),
                    "archived_at": datetime.utcnow().isoformat(),
                    "archived_by": str(current_user["id"])
                }
            
            elif batch_request.operation == "delete":
                # Soft delete
                document.status = "deleted"
                document.updated_at = datetime.utcnow()
                document.metadata = {
                    **(document.metadata or {}),
                    "deleted_at": datetime.utcnow().isoformat(),
                    "deleted_by": str(current_user["id"])
                }
            
            elif batch_request.operation == "extend":
                # Prolonger la durée de vie
                days = batch_request.parameters.get("days", 365)
                if document.expires_at:
                    document.expires_at = document.expires_at + timedelta(days=days)
                else:
                    document.expires_at = datetime.utcnow() + timedelta(days=days)
                
                document.updated_at = datetime.utcnow()
                document.metadata = {
                    **(document.metadata or {}),
                    "expiry_extended_at": datetime.utcnow().isoformat(),
                    "expiry_extended_by": str(current_user["id"]),
                    "expiry_extended_days": days
                }
            
            db.commit()
            successful_ids.append(doc_id)
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement par lot du document {doc_id}: {str(e)}")
            failed_ids.append(doc_id)
    
    return {
        "operation": batch_request.operation,
        "successful_ids": successful_ids,
        "failed_ids": failed_ids,
        "message": f"Opération terminée avec {len(successful_ids)} succès et {len(failed_ids)} échecs"
    }


# Routes pour les permissions
@app.post("/documents/{document_id}/permissions", response_model=PermissionResponse)
async def add_permission(
    document_id: uuid.UUID,
    permission: PermissionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ajoute une permission sur un document
    """
    # Vérifier l'existence du document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est admin du document
    has_permission = check_document_permission(db, document_id, current_user["id"], "admin")
    if not has_permission:
        raise HTTPException(status_code=403, detail="Vous n'avez pas les droits d'administration sur ce document")
    
    # Vérifier si la permission existe déjà
    existing_permission = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id,
        DocumentPermission.entity_type == permission.entity_type,
        DocumentPermission.entity_id == permission.entity_id,
        DocumentPermission.permission_type == permission.permission_type
    ).first()
    
    if existing_permission:
        # Mettre à jour la permission existante
        existing_permission.expires_at = permission.expires_at
        existing_permission.granted_by = current_user["id"]
        db.commit()
        db.refresh(existing_permission)
        return PermissionResponse.model_validate(existing_permission)
    
    # Créer une nouvelle permission
    new_permission = DocumentPermission(
        document_id=document_id,
        entity_type=permission.entity_type,
        entity_id=permission.entity_id,
        permission_type=permission.permission_type,
        expires_at=permission.expires_at,
        granted_by=current_user["id"]
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return PermissionResponse.model_validate(new_permission)


@app.get("/documents/{document_id}/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    document_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Liste les permissions d'un document
    """
    # Vérifier l'existence du document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur a accès au document
    has_permission = check_document_permission(db, document_id, current_user["id"], "read")
    if not has_permission:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Récupérer les permissions
    permissions = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id
    ).all()
    
    return [PermissionResponse.model_validate(p) for p in permissions]


@app.delete("/documents/{document_id}/permissions/{permission_id}")
async def remove_permission(
    document_id: uuid.UUID,
    permission_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime une permission d'un document
    """
    # Vérifier l'existence du document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est admin du document
    has_permission = check_document_permission(db, document_id, current_user["id"], "admin")
    if not has_permission:
        raise HTTPException(status_code=403, detail="Vous n'avez pas les droits d'administration sur ce document")
    
    # Récupérer la permission
    permission = db.query(DocumentPermission).filter(
        DocumentPermission.id == permission_id,
        DocumentPermission.document_id == document_id
    ).first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission non trouvée")
    
    # Empêcher la suppression de sa propre permission admin
    if (
        permission.entity_type == "user" and
        permission.entity_id == current_user["id"] and
        permission.permission_type == "admin"
    ):
        raise HTTPException(
            status_code=400,
            detail="Vous ne pouvez pas supprimer votre propre permission d'administration"
        )
    
    # Supprimer la permission
    db.delete(permission)
    db.commit()
    
    return {"status": "success", "message": "Permission supprimée avec succès"}


# Routes pour les logs d'accès
@app.get("/documents/{document_id}/access-logs", response_model=List[AccessLogResponse])
async def list_access_logs(
    document_id: uuid.UUID,
    limit: int = Query(50, gt=0, lt=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Liste les logs d'accès à un document (pour audit RGPD)
    """
    # Vérifier l'existence du document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est admin du document
    has_permission = check_document_permission(db, document_id, current_user["id"], "admin")
    if not has_permission:
        raise HTTPException(status_code=403, detail="Vous n'avez pas les droits d'administration sur ce document")
    
    # Récupérer les logs d'accès
    logs = db.query(DocumentAccessLog).filter(
        DocumentAccessLog.document_id == document_id
    ).order_by(
        DocumentAccessLog.timestamp.desc()
    ).limit(limit).all()
    
    return [AccessLogResponse.model_validate(log) for log in logs]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
