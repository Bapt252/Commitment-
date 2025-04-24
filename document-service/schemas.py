from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, UUID4
from datetime import datetime
import uuid


class DocumentBase(BaseModel):
    document_type: str = Field(..., description="Type de document (cv, cover_letter, job_description)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles du document")
    
    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ["cv", "cover_letter", "job_description"]
        if v not in allowed_types:
            raise ValueError(f"Le type de document doit être l'un des suivants: {', '.join(allowed_types)}")
        return v


class DocumentCreate(DocumentBase):
    expires_in_days: Optional[int] = Field(365, description="Durée en jours avant expiration (RGPD)")
    
    @validator('expires_in_days')
    def validate_expiry(cls, v):
        if v is not None and (v < 1 or v > 3650):  # Max 10 ans
            raise ValueError("La durée d'expiration doit être entre 1 et 3650 jours")
        return v


class DocumentResponse(DocumentBase):
    id: UUID4
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    version: int
    
    class Config:
        orm_mode = True


class DocumentDetailResponse(DocumentResponse):
    bucket_name: str
    object_key: str
    content_hash: str
    parsed_data_id: Optional[UUID4]
    
    class Config:
        orm_mode = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    limit: int
    pages: int


class PermissionBase(BaseModel):
    entity_type: str = Field(..., description="Type d'entité (user, service, role)")
    entity_id: UUID4 = Field(..., description="ID de l'entité")
    permission_type: str = Field(..., description="Type de permission (read, write, delete, admin)")
    expires_at: Optional[datetime] = Field(None, description="Date d'expiration de la permission")
    
    @validator('entity_type')
    def validate_entity_type(cls, v):
        allowed_types = ["user", "service", "role"]
        if v not in allowed_types:
            raise ValueError(f"Le type d'entité doit être l'un des suivants: {', '.join(allowed_types)}")
        return v
    
    @validator('permission_type')
    def validate_permission_type(cls, v):
        allowed_types = ["read", "write", "delete", "admin"]
        if v not in allowed_types:
            raise ValueError(f"Le type de permission doit être l'un des suivants: {', '.join(allowed_types)}")
        return v


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: UUID4
    document_id: UUID4
    granted_at: datetime
    granted_by: UUID4
    
    class Config:
        orm_mode = True


class AccessLogResponse(BaseModel):
    id: UUID4
    document_id: UUID4
    user_id: UUID4
    access_type: str
    timestamp: datetime
    ip_address: str
    user_agent: Optional[str]
    success: bool
    
    class Config:
        orm_mode = True


class PresignedUrlCreate(BaseModel):
    expires_in_seconds: Optional[int] = Field(300, description="Durée de validité en secondes")
    max_access_count: Optional[int] = Field(None, description="Nombre maximum d'accès autorisés")
    
    @validator('expires_in_seconds')
    def validate_expires(cls, v):
        if v < 1 or v > 86400:  # Max 24 heures
            raise ValueError("La durée de validité doit être entre 1 et 86400 secondes (24 heures)")
        return v
    
    @validator('max_access_count')
    def validate_max_access(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError("Le nombre maximum d'accès doit être entre 1 et 100")
        return v


class PresignedUrlResponse(BaseModel):
    id: Optional[UUID4] = None
    document_id: UUID4
    url: str
    expires_at: datetime
    max_access_count: Optional[int] = None
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime


class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None
    scopes: List[str] = []


class UserBaseResponse(BaseModel):
    id: UUID4
    email: str
    is_active: bool
    full_name: Optional[str] = None


class SecurityScanRequest(BaseModel):
    document_id: UUID4


class SecurityScanResponse(BaseModel):
    status: str
    document_id: UUID4
    infected: bool
    threat_name: Optional[str] = None
    timestamp: datetime


class DocumentBatchProcessRequest(BaseModel):
    document_ids: List[UUID4]
    operation: str = Field(..., description="Type d'opération (archive, delete, extend)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres spécifiques à l'opération")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_ops = ["archive", "delete", "extend"]
        if v not in allowed_ops:
            raise ValueError(f"L'opération doit être l'une des suivantes: {', '.join(allowed_ops)}")
        return v


class DocumentBatchProcessResponse(BaseModel):
    operation: str
    successful_ids: List[UUID4]
    failed_ids: List[UUID4]
    message: str
