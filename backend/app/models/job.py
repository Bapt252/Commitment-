from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ARRAY, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY as PGARRAY
from sqlalchemy.ext.mutable import MutableList
from app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    requirements = Column(Text)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    location = Column(String, index=True)
    company_id = Column(Integer, index=True, nullable=True)
    job_type = Column(String)  # full-time, part-time, contract, etc.
    experience_level = Column(String)  # entry, mid, senior, etc.
    skills = Column(MutableList.as_mutable(PGARRAY(String)), default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())