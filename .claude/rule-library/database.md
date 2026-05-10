## Migrations

- Every migration must have both `up` and `down` scripts; untested rollbacks are not rollbacks
- Apply schema changes in two phases: (1) backward-compatible deploy, (2) cleanup after old code is retired
  - Example: adding a NOT NULL column → add nullable first, backfill, then add constraint in a later migration
- Never rename a column or table in a single migration — add the new name, migrate data, drop the old name across separate deploys
- Migration files are immutable once applied to any non-local environment; create a new migration to correct a mistake

## Rollback Safety

- A schema state must be compatible with the previous application version at all times
- Dropping a column or table requires a deprecation period: mark it unused in code, deploy, then drop in a later migration
- Foreign key additions must not reference data that may not exist; populate the relationship before adding the constraint
- Index creation on large tables must use `CREATE INDEX CONCURRENTLY` (PostgreSQL) or equivalent non-blocking DDL

## Large Table Operations

- Never run a full-table `ALTER TABLE` that locks rows in production without a maintenance window or online DDL tool
- Backfills on tables > 1M rows must be batched: update in chunks of 1,000–10,000 rows with a `WHERE id > last_id` cursor
- Adding a non-nullable column with a default requires measuring lock duration on a staging replica first
- Test migrations against a production-sized dataset before deploying

## Query Design

- Never load unbounded result sets — always apply `LIMIT` and use cursor-based pagination for large collections
- Avoid N+1 queries: use eager loading (JOIN or batch fetch) when accessing related records in a loop
- Use query analysis tools (`EXPLAIN ANALYZE`) on any query that touches more than 10,000 rows before shipping
- Parameterized queries only — no string concatenation for SQL

## Index Strategy

- Add an index for every foreign key unless the table has fewer than 1,000 rows
- Composite indexes: put the most selective column first; align column order with the most common `WHERE` clause
- Do not add indexes speculatively — measure query performance first; each index slows writes
- Drop unused indexes: query `pg_stat_user_indexes` (PostgreSQL) or equivalent monthly

## Data Integrity

- Enforce referential integrity at the database level (foreign keys), not only in application code
- Use database-level NOT NULL, UNIQUE, and CHECK constraints as a last line of defense
- Never delete records that other records reference — soft delete (set `deleted_at`) or cascade explicitly
- PII and sensitive fields must be encrypted at rest at the column level or database level
