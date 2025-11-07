# Database Migrations Guide

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

## Overview

Alembic is a lightweight database migration tool for use with SQLAlchemy. It provides a way to manage database schema changes in a version-controlled manner.

## Prerequisites

- Python virtual environment activated
- All dependencies installed (`pip install -r requirements.txt`)

## Common Commands

### Apply Migrations

Apply all pending migrations to the database:
```bash
alembic upgrade head
```

### Check Current Migration

Check which migration version is currently applied:
```bash
alembic current
```

### View Migration History

Show all migrations and their status:
```bash
alembic history --verbose
```

### Rollback Migrations

Rollback to a specific migration:
```bash
alembic downgrade <revision>
```

Rollback all migrations:
```bash
alembic downgrade base
```

Rollback one migration:
```bash
alembic downgrade -1
```

## Creating New Migrations

### Auto-generate Migration

Alembic can automatically detect changes to your models and generate migrations:

```bash
alembic revision --autogenerate -m "Description of changes"
```

**Important:** Always review auto-generated migrations before applying them. Alembic might not detect all changes correctly.

### Manual Migration

Create an empty migration file for manual editing:

```bash
alembic revision -m "Description of changes"
```

## Migration Best Practices

1. **Always review generated migrations** - Auto-generated migrations may not be perfect
2. **Test migrations** - Test both upgrade and downgrade before committing
3. **One logical change per migration** - Keep migrations focused and atomic
4. **Never modify applied migrations** - Create a new migration to fix issues
5. **Backup your data** - Always backup before running migrations in production
6. **Use descriptive messages** - Make migration purposes clear in the message

## Example Workflow

### Adding a New Column

1. Modify your model:
```python
# app/models/user.py
class User(Base):
    # ... existing fields
    bio = Column(String(500), nullable=True)  # New field
```

2. Generate migration:
```bash
alembic revision --autogenerate -m "Add bio field to User model"
```

3. Review the generated file in `app/migrations/versions/`

4. Apply the migration:
```bash
alembic upgrade head
```

### Rolling Back a Migration

If something goes wrong:

```bash
# Rollback the last migration
alembic downgrade -1

# Or rollback to a specific version
alembic downgrade <revision_id>
```

## Migration Files Location

Migration files are stored in: `app/migrations/versions/`

Each migration file contains:
- `upgrade()` - Function to apply the migration
- `downgrade()` - Function to rollback the migration
- Revision ID and dependencies

## Initial Setup (Already Done)

The initial migration has been created and includes all base tables:
- `users` - User accounts
- `media` - Base media table (polymorphic)
- `movies`, `series`, `anime`, `manga`, `books`, `games` - Media type tables
- `tags` - Tag system
- `media_tags` - Many-to-many relationship
- `tracking` - User tracking entries

Revision: `cf0cba7315c7` - "Initial migration"

## Troubleshooting

### Migration Conflicts

If you get conflicts when pulling changes:
1. Rollback your local migration
2. Pull latest changes
3. Regenerate your migration if needed

### Database Out of Sync

If Alembic thinks the database is out of sync:

```bash
# Stamp the database with the current migration
alembic stamp head
```

**Warning:** Only use this if you're sure the database schema matches the migration.

### Fresh Start

To reset the database completely:

```bash
# Rollback all migrations
alembic downgrade base

# Reapply all migrations
alembic upgrade head
```

## Production Deployment

For production deployments:

1. **Backup the database first**:
```bash
# For SQLite
cp production.db production.db.backup

# For PostgreSQL
pg_dump dbname > backup.sql
```

2. **Apply migrations**:
```bash
alembic upgrade head
```

3. **Verify** the migration was successful
4. **Test** the application

## Configuration

Migration configuration is in:
- `alembic.ini` - Alembic configuration
- `app/migrations/env.py` - Migration environment setup

The database URL is automatically loaded from your `.env` file via `app/core/config.py`.

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
