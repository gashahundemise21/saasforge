# 2. Soft Deletes

Date: 2024-05-24

## Status
Accepted

## Context
When users delete organizations, projects, or users, we want to retain the data for audit purposes and potential recovery, rather than permanently destroying records.

## Decision
We will implement soft deletes using a `deleted_at` timestamp column.
- Core entities (e.g., Organization, Project, User) will include this column.
- Queries must filter `where(deleted_at.is_(None))`.
- The `Task` entity is excluded from soft deletes because it is highly volatile and frequently deleted/created, leading to unbounded table growth and index bloat.

## Consequences
- **Pros**: Easy data recovery, full audit trail, referential integrity is maintained.
- **Cons**: Unique constraints may conflict with soft-deleted rows. Queries must always remember to filter out deleted rows.
