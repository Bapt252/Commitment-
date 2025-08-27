from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base


class MatchQualityEnum(enum.Enum):
    VERY_GOOD = "très bon"
    GOOD = "bon"
    MEDIUM = "moyen"
    POOR = "faible"
    UNACCEPTABLE = "inacceptable"


class MatchFeedback(Base):
    __tablename__ = 'match_feedbacks'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    match_id = Column(UUID(as_uuid=True), ForeignKey('match_results.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_type = Column(String(20), nullable=False)  # 'recruiter' ou 'candidate'
    rating = Column(Integer, nullable=False)
    match_quality = Column(Enum(MatchQualityEnum), nullable=False)
    comment = Column(Text, nullable=True)
    algorithm_version = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    match_result = relationship("MatchResult", backref="feedbacks")

    # Contraintes
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return f"<MatchFeedback {self.id} - Match: {self.match_id}, User: {self.user_id}, Rating: {self.rating}>"