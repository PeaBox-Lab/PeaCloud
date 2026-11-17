# Database migrations
v0.12 introduces the production PostgreSQL boundary through SQLAlchemy. The current schema bootstrap is intentionally small. Before adding persistent tenants/resources, adopt Alembic and require forward/backward migration tests on every schema change.
