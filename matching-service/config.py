import os
from datetime import datetime

# ... existing config ...

ALGORITHM_VERSION = os.getenv("ALGORITHM_VERSION", "v1.0.0")

def get_algorithm_version() -> str:
    """Retourne la version actuelle de l'algorithme de matching."""
    # Vous pouvez personnaliser cette logique selon vos besoins
    # Par exemple, inclure la date de déploiement
    deploy_date = datetime.now().strftime("%Y%m%d")
    return f"{ALGORITHM_VERSION}-{deploy_date}"