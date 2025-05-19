"""
Services Package
===============
Services externes pour le système SmartMatch (NLP, embeddings, etc.)
"""

from .embeddings_service import EmbeddingsService
from .skills_embeddings_db import SkillsEmbeddingsDB

__all__ = ['EmbeddingsService', 'SkillsEmbeddingsDB']
