"""
Custom Exceptions for SmartMatcher
---------------------------------
Définit les exceptions personnalisées utilisées dans le système de matching.
"""


class SmartMatchError(Exception):
    """Exception de base pour tous les erreurs du SmartMatcher"""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code or "SMART_MATCH_ERROR"
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> dict:
        """Convertit l'exception en dictionnaire pour la sérialisation"""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(SmartMatchError):
    """Erreur de configuration du système de matching"""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details={"config_key": config_key} if config_key else {}
        )


class ValidationError(SmartMatchError):
    """Erreur de validation des données"""
    
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": str(value)} if field else {}
        )


class ServiceError(SmartMatchError):
    """Erreur liée à un service externe (API, base de données, etc.)"""
    
    def __init__(self, message: str, service_name: str = None, status_code: int = None):
        super().__init__(
            message=message,
            code="SERVICE_ERROR",
            details={
                "service_name": service_name,
                "status_code": status_code
            }
        )


class CacheError(ServiceError):
    """Erreur spécifique au service de cache"""
    
    def __init__(self, message: str, cache_key: str = None):
        super().__init__(
            message=message,
            service_name="cache",
            details={"cache_key": cache_key}
        )


class NLPServiceError(ServiceError):
    """Erreur spécifique au service NLP"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(
            message=message,
            service_name="nlp",
            details={"operation": operation}
        )


class LocationServiceError(ServiceError):
    """Erreur spécifique au service de géolocalisation"""
    
    def __init__(self, message: str, location: str = None):
        super().__init__(
            message=message,
            service_name="location",
            details={"location": location}
        )


class MatchingEngineError(SmartMatchError):
    """Erreur du moteur de matching"""
    
    def __init__(self, message: str, candidate_id: str = None, job_id: str = None):
        super().__init__(
            message=message,
            code="MATCHING_ENGINE_ERROR",
            details={
                "candidate_id": candidate_id,
                "job_id": job_id
            }
        )


class MatcherError(SmartMatchError):
    """Erreur d'un matcher spécifique"""
    
    def __init__(self, message: str, matcher_name: str = None):
        super().__init__(
            message=message,
            code="MATCHER_ERROR",
            details={"matcher_name": matcher_name}
        )


class ScoringError(SmartMatchError):
    """Erreur lors du calcul de score"""
    
    def __init__(self, message: str, strategy_name: str = None):
        super().__init__(
            message=message,
            code="SCORING_ERROR",
            details={"strategy_name": strategy_name}
        )


class PerformanceError(SmartMatchError):
    """Erreur liée aux performances (timeout, limite de mémoire, etc.)"""
    
    def __init__(self, message: str, operation: str = None, duration_ms: float = None):
        super().__init__(
            message=message,
            code="PERFORMANCE_ERROR",
            details={
                "operation": operation,
                "duration_ms": duration_ms
            }
        )


class DataNotFoundError(SmartMatchError):
    """Erreur lorsque des données requises ne sont pas trouvées"""
    
    def __init__(self, message: str, data_type: str = None, data_id: str = None):
        super().__init__(
            message=message,
            code="DATA_NOT_FOUND",
            details={
                "data_type": data_type,
                "data_id": data_id
            }
        )


class BatchProcessingError(SmartMatchError):
    """Erreur lors du traitement en lot"""
    
    def __init__(self, message: str, batch_size: int = None, processed_count: int = None):
        super().__init__(
            message=message,
            code="BATCH_PROCESSING_ERROR",
            details={
                "batch_size": batch_size,
                "processed_count": processed_count
            }
        )


# Helper functions pour la gestion d'erreurs

def handle_service_error(func):
    """Décorateur pour gérer les erreurs de service"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ServiceError:
            raise  # Re-lever les erreurs de service telles quelles
        except Exception as e:
            raise ServiceError(
                message=f"Erreur inattendue dans {func.__name__}: {str(e)}",
                service_name=func.__module__.split('.')[-1]
            )
    return wrapper


def validate_candidate(candidate) -> None:
    """Valide les données d'un candidat"""
    if not candidate:
        raise ValidationError("Candidat manquant")
    
    if not candidate.id:
        raise ValidationError("ID candidat manquant", field="id")
    
    if not candidate.name:
        raise ValidationError("Nom candidat manquant", field="name")
    
    if candidate.experience_years < 0:
        raise ValidationError(
            "Années d'expérience invalides",
            field="experience_years",
            value=candidate.experience_years
        )


def validate_job(job) -> None:
    """Valide les données d'une offre d'emploi"""
    if not job:
        raise ValidationError("Offre d'emploi manquante")
    
    if not job.id:
        raise ValidationError("ID offre manquant", field="id")
    
    if not job.title:
        raise ValidationError("Titre offre manquant", field="title")
    
    if not job.company_name:
        raise ValidationError("Nom entreprise manquant", field="company_name")
    
    if job.min_experience_years < 0:
        raise ValidationError(
            "Expérience minimale invalide",
            field="min_experience_years",
            value=job.min_experience_years
        )
    
    if (job.max_experience_years is not None and 
        job.max_experience_years < job.min_experience_years):
        raise ValidationError(
            "Expérience maximale inférieure au minimum",
            field="max_experience_years"
        )


def validate_match_result(result) -> None:
    """Valide un résultat de match"""
    if not result:
        raise ValidationError("Résultat de match manquant")
    
    if not result.candidate_id:
        raise ValidationError("ID candidat manquant", field="candidate_id")
    
    if not result.job_id:
        raise ValidationError("ID offre manquant", field="job_id")
    
    if not (0 <= result.overall_score <= 1):
        raise ValidationError(
            "Score global invalide (doit être entre 0 et 1)",
            field="overall_score",
            value=result.overall_score
        )
    
    # Valider les scores par catégorie
    for category, score in result.category_scores.items():
        if not (0 <= score <= 1):
            raise ValidationError(
                f"Score categorie '{category}' invalide (doit être entre 0 et 1)",
                field=f"category_scores.{category}",
                value=score
            )
