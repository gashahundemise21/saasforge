.PHONY: up down restart test lint format check shell db-shell

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d

test:
	cd backend && pytest

lint:
	cd backend && ruff check .
	cd backend && mypy app tests
	cd backend && bandit -r app

format:
	cd backend && ruff format .
	cd backend && ruff check --fix .

check: format lint test

shell:
	cd backend && python -m app.main

db-shell:
	docker-compose exec postgres psql -U postgres -d saasforge
