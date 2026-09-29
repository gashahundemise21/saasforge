# 1. Multi-Tenancy Strategy

Date: 2024-05-24

## Status
Accepted

## Context
We need to support multiple organizations in a single deployment of SaaSForge. Data must be strictly isolated between tenants, but we want to minimize infrastructure overhead.

## Decision
We will use **Row-Level Logical Isolation**.
- A single PostgreSQL database and schema will be shared by all tenants.
- Every core table will have an `organization_id` foreign key.
- API endpoints will require an `X-Organization-Slug` or `X-API-Key` to resolve the tenant context.
- Database queries must explicitly filter by `organization_id`.

## Consequences
- **Pros**: Easy to maintain, simple migrations, cost-effective.
- **Cons**: Requires strict discipline in backend services to never forget the `organization_id` filter (risk of cross-tenant data leaks).
