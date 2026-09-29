# Development Guide

## Prerequisites
- Node.js >= 20
- Python >= 3.12
- Docker & Docker Compose
- `uv` package manager (for Python dependencies)

## Running Locally
1. Start the database and Redis:
   ```bash
   docker-compose up -d
   ```
2. Start the backend server:
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload --port 8000
   ```
3. Start the frontend server:
   ```bash
   cd frontend
   npm run dev
   ```

## Database Migrations
To create a new migration after changing SQLAlchemy models:
```bash
cd backend
uv run alembic revision --autogenerate -m "description"
```
To apply migrations:
```bash
uv run alembic upgrade head
```

## Linting and Formatting
- **Backend**: We use `ruff` for fast linting and formatting.
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```
- **Frontend**: We use `eslint` and `prettier`.
  ```bash
  npm run lint
  ```
