# Variables
APP_NAME = intelligent-search-bar
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.prod.yml

# Development commands
.PHONY: build
build:
	$(DOCKER_COMPOSE) build

.PHONY: up
up:
	$(DOCKER_COMPOSE) up

.PHONY: down
down:
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: shell
shell:
	$(DOCKER_COMPOSE) exec web bash

.PHONY: test
test:
	$(DOCKER_COMPOSE) run --rm web pytest

# Production commands
.PHONY: prod-build
prod-build:
	$(DOCKER_COMPOSE_PROD) build

.PHONY: prod-up
prod-up:
	$(DOCKER_COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down:
	$(DOCKER_COMPOSE_PROD) down

.PHONY: prod-logs
prod-logs:
	$(DOCKER_COMPOSE_PROD) logs -f

# Database commands
.PHONY: db-shell
db-shell:
	$(DOCKER_COMPOSE) exec db psql -U $(DB_USER) -d $(DB_NAME)

.PHONY: migrate
migrate:
	$(DOCKER_COMPOSE) exec web python -m alembic upgrade head

# Cleanup commands
.PHONY: clean
clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "Development:"
	@echo "  make build      - Build development containers"
	@echo "  make up         - Start development environment"
	@echo "  make down       - Stop development environment"
	@echo "  make logs       - View logs"
	@echo "  make shell      - Access web container shell"
	@echo "  make test       - Run tests"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build - Build production containers"
	@echo "  make prod-up    - Start production environment"
	@echo "  make prod-down  - Stop production environment"
	@echo "  make prod-logs  - View production logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell   - Access database shell"
	@echo "  make migrate    - Run database migrations"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove containers and cleanup"