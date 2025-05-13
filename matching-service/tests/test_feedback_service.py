import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.feedback_service import FeedbackService
from schemas.feedback import FeedbackCreate, MatchQualityEnum
from models.feedback import MatchFeedback
from models.match_result import MatchResult


@pytest.fixture
def mock_db():
    return Mock(spec=Session)


@pytest.fixture
def feedback_service(mock_db):
    return FeedbackService(mock_db)


@pytest.fixture
def sample_feedback_payload():
    return FeedbackCreate(
        match_id=uuid4(),
        rating=4,
        match_quality=MatchQualityEnum.GOOD,
        comment="Bon match, profil correspondant aux attentes"
    )


class TestFeedbackService:
    @pytest.mark.asyncio
    async def test_save_feedback_success(self, feedback_service, mock_db, sample_feedback_payload):
        # Arrange
        match_id = sample_feedback_payload.match_id
        user_id = uuid4()
        user_type = "recruiter"
        
        # Mock match_result existe
        mock_match_result = Mock(spec=MatchResult)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_match_result
        
        # Mock pas de feedback existant
        mock_db.query.return_value.filter.side_effect = [
            Mock(first=Mock(return_value=mock_match_result)),
            Mock(first=Mock(return_value=None))
        ]
        
        # Act
        result = await feedback_service.save_feedback(
            match_id=match_id,
            user_id=user_id,
            user_type=user_type,
            payload=sample_feedback_payload
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert isinstance(result.id, uuid4().__class__)
        assert result.rating == sample_feedback_payload.rating
        
    @pytest.mark.asyncio
    async def test_save_feedback_match_not_found(self, feedback_service, mock_db, sample_feedback_payload):
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await feedback_service.save_feedback(
                match_id=sample_feedback_payload.match_id,
                user_id=uuid4(),
                user_type="recruiter",
                payload=sample_feedback_payload
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_save_feedback_already_exists(self, feedback_service, mock_db, sample_feedback_payload):
        # Arrange
        mock_match_result = Mock(spec=MatchResult)
        mock_existing_feedback = Mock(spec=MatchFeedback)
        
        mock_db.query.return_value.filter.side_effect = [
            Mock(first=Mock(return_value=mock_match_result)),
            Mock(first=Mock(return_value=mock_existing_feedback))
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await feedback_service.save_feedback(
                match_id=sample_feedback_payload.match_id,
                user_id=uuid4(),
                user_type="recruiter",
                payload=sample_feedback_payload
            )
        
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_feedback_stats(self, feedback_service, mock_db):
        # Arrange
        mock_feedbacks = [
            Mock(rating=5, match_quality=MatchQualityEnum.VERY_GOOD, created_at=datetime.now()),
            Mock(rating=4, match_quality=MatchQualityEnum.GOOD, created_at=datetime.now()),
            Mock(rating=3, match_quality=MatchQualityEnum.MEDIUM, created_at=datetime.now())
        ]
        
        mock_db.query.return_value.all.return_value = mock_feedbacks
        
        # Act
        stats = await feedback_service.get_feedback_stats()
        
        # Assert
        assert stats["average_rating"] == 4.0
        assert stats["total_feedbacks"] == 3
        assert len(stats["quality_distribution"]) > 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])