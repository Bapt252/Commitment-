import uuid
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy import Column, String, Integer, TIMESTAMP, Boolean, ForeignKey, BigInteger, JSON, ARRAY, Index
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    bucket_name = Column(String(100), nullable=False)
    object_key = Column(String(255), nullable=False)
    content_hash = Column(String(64), nullable=False)
    encryption_key_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    document_type = Column(String(50), nullable=False)
    parsed_data_id = Column(UUID(as_uuid=True), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    metadata = Column(JSONB, nullable=True)

    # Relations
    permissions = relationship("DocumentPermission", back_populates="document", cascade="all, delete-orphan")
    access_logs = relationship("DocumentAccessLog", back_populates="document", cascade="all, delete-orphan")
    presigned_urls = relationship("PresignedUrl", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_documents_type_status', document_type, status),
        Index('idx_documents_expiry', expires_at, postgresql_where=expires_at.isnot(None)),
    )


class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(20), nullable=False)  # user, service, role
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    permission_type = Column(String(20), nullable=False)  # read, write, delete, admin
    granted_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    granted_by = Column(UUID(as_uuid=True), nullable=False)

    # Relations
    document = relationship("Document", back_populates="permissions")

    # Indexes
    __table_args__ = (
        Index('idx_permissions_entity', entity_type, entity_id),
        {'sqlite_autoincrement': True}
    )
    
    # Contrainte d'unicité
    __table_args__ = (
        {'sqlite_autoincrement': True},
        {'unique': (document_id, entity_type, entity_id, permission_type)}
    )


class DocumentAccessLog(Base):
    __tablename__ = "document_access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    access_type = Column(String(20), nullable=False)  # view, download, update, delete
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    ip_address = Column(INET, nullable=False)
    user_agent = Column(String, nullable=True)
    request_id = Column(UUID(as_uuid=True), nullable=False)
    success = Column(Boolean, nullable=False)

    # Relations
    document = relationship("Document", back_populates="access_logs")

    # Indexes
    __table_args__ = (
        Index('idx_access_logs_document', document_id, timestamp),
        Index('idx_access_logs_user', user_id, timestamp),
    )


class PresignedUrl(Base):
    __tablename__ = "presigned_urls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    access_count = Column(Integer, nullable=False, default=0)
    max_access_count = Column(Integer, nullable=True)
    is_revoked = Column(Boolean, nullable=False, default=False)

    # Relations
    document = relationship("Document", back_populates="presigned_urls")

    # Indexes
    __table_args__ = (
        Index('idx_presigned_urls_document', document_id),
        Index('idx_presigned_urls_expiry', expires_at),
    )
