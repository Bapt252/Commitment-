"""
Proxy HTTP intelligent pour rediriger les requêtes vers les microservices
Avec circuit breaker, retry automatique et load balancing
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

import httpx
from fastapi import HTTPException, Request, status
from fastapi.responses import Response

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"      # Fonctionnement normal
    OPEN = "open"          # Service en panne
    HALF_OPEN = "half_open"  # Test de récupération

@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3

@dataclass
class CircuitBreaker:
    """Circuit breaker pour la résilience"""
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0
    success_count: int = 0
    
    def can_execute(self) -> bool:
        """Vérifier si une requête peut être exécutée"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker passage en HALF_OPEN")
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False
    
    def record_success(self):
        """Enregistrer un succès"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker retour à CLOSED")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Enregistrer un échec"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker retour à OPEN")
        elif (self.state == CircuitState.CLOSED and 
              self.failure_count >= self.config.failure_threshold):
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker passage à OPEN")

class ServiceProxy:
    """Proxy pour un service avec load balancing et résilience"""
    
    def __init__(self, service_name: str, urls: List[str]):
        self.service_name = service_name
        self.urls = urls
        self.current_url_index = 0
        self.circuit_breakers = {url: CircuitBreaker() for url in urls}
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.HTTP_TIMEOUT),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
    
    def get_next_url(self) -> Optional[str]:
        """Obtenir la prochaine URL disponible (load balancing round-robin)"""
        attempts = 0
        while attempts < len(self.urls):
            url = self.urls[self.current_url_index]
            self.current_url_index = (self.current_url_index + 1) % len(self.urls)
            
            circuit_breaker = self.circuit_breakers[url]
            if circuit_breaker.can_execute():
                return url
            
            attempts += 1
        
        logger.error(f"Aucune URL disponible pour {self.service_name}")
        return None
    
    async def forward_request(
        self, 
        path: str, 
        method: str, 
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        data: bytes = None,
        files: Dict = None,
        json: Dict = None
    ) -> Response:
        """Rediriger une requête vers le service avec retry automatique"""
        
        last_exception = None
        
        for attempt in range(len(self.urls)):
            url = self.get_next_url()
            if not url:
                break
            
            circuit_breaker = self.circuit_breakers[url]
            full_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
            
            try:
                logger.debug(f"Tentative {attempt + 1}: {method} {full_url}")
                
                # Préparer les headers
                request_headers = headers.copy() if headers else {}
                # Supprimer les headers problématiques
                request_headers.pop("host", None)
                request_headers.pop("content-length", None)
                
                # Faire la requête
                response = await self.client.request(
                    method=method,
                    url=full_url,
                    headers=request_headers,
                    params=params,
                    content=data,
                    files=files,
                    json=json,
                    follow_redirects=False
                )
                
                # Enregistrer le succès
                circuit_breaker.record_success()
                
                logger.debug(f"Succès: {method} {full_url} -> {response.status_code}")
                
                # Retourner la réponse
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type")
                )
                
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as e:
                logger.warning(f"Erreur réseau vers {full_url}: {e}")
                circuit_breaker.record_failure()
                last_exception = e
                continue
                
            except httpx.HTTPStatusError as e:
                logger.warning(f"Erreur HTTP vers {full_url}: {e.response.status_code}")
                if e.response.status_code >= 500:
                    circuit_breaker.record_failure()
                    last_exception = e
                    continue
                else:
                    # Erreur client (4xx), on retourne la réponse
                    return Response(
                        content=e.response.content,
                        status_code=e.response.status_code,
                        headers=dict(e.response.headers)
                    )
                    
            except Exception as e:
                logger.error(f"Erreur inattendue vers {full_url}: {e}")
                circuit_breaker.record_failure()
                last_exception = e
                continue
        
        # Tous les services sont en panne
        logger.error(f"Échec de toutes les tentatives pour {self.service_name}")
        
        if last_exception:
            if isinstance(last_exception, httpx.TimeoutException):
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"Timeout du service {self.service_name}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service {self.service_name} indisponible"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {self.service_name} indisponible"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier l'état de santé du service"""
        results = {}
        
        for url in self.urls:
            try:
                response = await self.client.get(
                    f"{url}/health",
                    timeout=settings.SERVICE_TIMEOUT
                )
                results[url] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "circuit_breaker": self.circuit_breakers[url].state.value
                }
            except Exception as e:
                results[url] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "circuit_breaker": self.circuit_breakers[url].state.value
                }
        
        return results
    
    async def close(self):
        """Fermer le client HTTP"""
        await self.client.aclose()

class ProxyManager:
    """Gestionnaire central des proxies vers les microservices"""
    
    def __init__(self):
        self.proxies: Dict[str, ServiceProxy] = {}
        self._setup_proxies()
    
    def _setup_proxies(self):
        """Configurer les proxies pour chaque service"""
        
        # CV Parser Service
        self.proxies["cv_parser"] = ServiceProxy(
            service_name="CV Parser",
            urls=[settings.CV_PARSER_URL]
        )
        
        # Job Parser Service  
        self.proxies["job_parser"] = ServiceProxy(
            service_name="Job Parser",
            urls=[settings.JOB_PARSER_URL]
        )
        
        # Matching Service
        self.proxies["matching"] = ServiceProxy(
            service_name="Matching Service",
            urls=[settings.MATCHING_SERVICE_URL]
        )
    
    def get_proxy(self, service_name: str) -> ServiceProxy:
        """Obtenir le proxy pour un service"""
        proxy = self.proxies.get(service_name)
        if not proxy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service {service_name} non trouvé"
            )
        return proxy
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Vérifier l'état de tous les services"""
        results = {}
        
        tasks = [
            (name, proxy.health_check()) 
            for name, proxy in self.proxies.items()
        ]
        
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                results[name] = {"error": str(e)}
        
        return results
    
    async def close_all(self):
        """Fermer tous les proxies"""
        for proxy in self.proxies.values():
            await proxy.close()

# Instance globale du gestionnaire de proxy
proxy_manager = ProxyManager()

async def forward_to_service(
    service_name: str,
    path: str,
    request: Request,
    body: bytes = None
) -> Response:
    """
    Fonction utilitaire pour rediriger une requête vers un service
    """
    proxy = proxy_manager.get_proxy(service_name)
    
    # Préparer les headers
    headers = dict(request.headers)
    
    # Préparer les paramètres
    params = dict(request.query_params) if request.query_params else None
    
    return await proxy.forward_request(
        path=path,
        method=request.method,
        headers=headers,
        params=params,
        data=body
    )
