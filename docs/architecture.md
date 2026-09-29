# SaaSForge Architecture

## Overview
SaaSForge is a multi-tenant B2B SaaS application built with a modern, decoupled architecture.
- **Frontend**: Next.js 15 (React), Tailwind CSS v4, Base UI, hosted/static.
- **Backend**: FastAPI (Python), SQLAlchemy 2.0 (async), PostgreSQL, Redis.
- **Infrastructure**: Dockerized, CI/CD via GitHub Actions.

## Multi-Tenancy Model
The application uses a **Logical Isolation (Row-Level)** multi-tenancy model.
- Every core entity (Project, Task, Team, AuditLog) belongs to an `Organization`.
- The `organization_id` foreign key is indexed and required.
- API endpoints require an `X-Organization-Slug` header (for user-based JWT access) or `X-API-Key` (for programmatic access) to resolve the tenant context.

## Authentication & Authorization
- **JWT**: Users authenticate via email/password and receive a JWT access token.
- **API Keys**: Organizations can generate API keys for programmatic access.
- **Role-Based Access Control (RBAC)**: Users are assigned roles (e.g., Owner, Admin, Member) within an Organization. Middleware enforces these roles for protected endpoints.

## Database Design
- **Soft Deletes**: Most entities use a `deleted_at` timestamp. `Task` is an exception for performance/cleanliness reasons.
- **Async SQLAlchemy**: All database access is fully asynchronous using `asyncpg`.
- **Migrations**: Alembic manages schema changes.

## Error Handling
- The backend uses standard FastAPI exception handlers.
- The frontend uses React Error Boundaries (`error.tsx`) to catch and report runtime errors gracefully.
