.PHONY: help dev-up dev-down test lint format build

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

dev-up: ## Démarrer l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Services démarrés. Accédez à:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - API: http://localhost:5050"
	@echo "  - Grafana: http://localhost:3001"
	@echo "  - Jupyter: http://localhost:8888"

dev-down: ## Arrêter l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-build: ## Reconstruire les images de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

test: ## Exécuter tous les tests
	poetry run pytest -v --cov=. --cov-report=html

test-integration: ## Exécuter les tests d'intégration
	poetry run pytest tests/integration/ -v

lint: ## Vérifier la qualité du code
	poetry run black --check .
	poetry run flake8 .
	poetry run bandit -r .

format: ## Formater le code
	poetry run black .
	poetry run isort .

security: ## Scanner les vulnérabilités
	poetry run safety check
	poetry run bandit -r .

install: ## Installer les dépendances
	poetry install

update: ## Mettre à jour les dépendances
	poetry update

migration: ## Exécuter les migrations de base de données
	docker-compose exec api alembic upgrade head

logs: ## Voir les logs de tous les services
	docker-compose logs -f

monitoring: ## Ouvrir les interfaces de monitoring
	@echo "Ouverture des interfaces de monitoring..."
	open http://localhost:3001  # Grafana
	open http://localhost:9090  # Prometheus
	open http://localhost:5601  # Kibana

performance-test: ## Exécuter les tests de performance
	poetry run locust -f tests/performance/locustfile.py --host=http://localhost:5050