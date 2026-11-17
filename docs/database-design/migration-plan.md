# WBS-14.7 · Migration plan

Proposed tool: Alembic with SQLAlchemy metadata for ordinary DDL and explicit reviewed SQL for PostgreSQL-specific objects. Store configuration and migration revisions under `backend/`. Use one revision chain and inspect generated migrations for extension, index and constraint changes.

| Order | Revision scope | Verification |
|---|---|---|
| 001 | Enable vector extension, add institutions, users and profile foundation | Clean upgrade; invalid roles and duplicate normalized identities fail |
| 002 | Add opportunity requirements, boards and application state | FK, scoped uniqueness and workflow fixtures |
| 003 | Add source registry, import tracking, catalogue records and links | Repeat import, invalid input, failed source and archival checks |
| 004+ | Add CV, discussions, moderation, ledger, quota, notifications and module-specific search as tables become available | Privacy deletion, balanced concurrent transfers, event deduplication and query checks |

WBS-14.3 should establish PostgreSQL/pgvector, Alembic and the agreed starter schema. Include the first searchable tables and their GIN indexes when introduced. Keep vector dimension and model provenance fixed from ADR-0002, pending provider approval. Give migrations a dedicated deploy step and serialize deployment migrations. Application credentials get only runtime permissions.

Review each revision with the table owners before merge. Validate on PostgreSQL with pgvector in CI and the local Docker stack. Run upgrade from empty, load idempotent fictional seed data, check constraints, downgrade to the preceding revision, then upgrade again. Also upgrade from a seeded previous revision and assert existing rows survive. Keep demo fixtures separate from migrations and production data.

For a populated deployment, expand schema first, backfill in restartable batches, validate constraints, deploy readers/writers, then remove old fields in a later revision. For destructive changes, document a forward recovery revision or tested backup restore. Before staging rollout, take a backup and exercise restore in a separate database. Prefer rolling back application code with compatible schema during incidents. Add large indexes concurrently only when needed and use Alembic's autocommit support for that operation.
