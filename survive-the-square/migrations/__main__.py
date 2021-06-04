"""Run migrations from the command line."""
import argparse
import importlib
import sys

from playhouse.migrate import SqliteMigrator

from bot.models.database import db


migrator = SqliteMigrator(db)

MIGRATIONS = [
]


def display_migrations():
    """Display a list of migrations to stdout."""
    print('You can specify a migration by name or ID:\n')
    for migration in MIGRATIONS:
        raw_number, *name_parts = migration.split('_')
        name = '-'.join(name_parts)
        number = raw_number.lstrip('0')
        print(f'{number:>3}: {name}')


def get_migration_by_id(migration_id: int) -> str:
    """Get a migration by its ID."""
    for migration in MIGRATIONS:
        check_id = migration.split('_')[0].lstrip('0')
        if check_id == str(migration_id):
            return migration
    raise ValueError(f'No migration found by ID {migration_id}.')


def get_migration_by_name(raw_name: str) -> str:
    """Get a migration by its name."""
    name = raw_name.replace('_', '-')    # Allow either.
    for migration in MIGRATIONS:
        check_name = '-'.join(migration.split('_')[1:])
        if check_name == name:
            return migration
    raise ValueError(f'No migration found by name {name}.')


def parse_migrations(raw_migrations: list[str]) -> list[str]:
    """Parse a list of migrations from the command line."""
    migrations = []
    for raw_migration in raw_migrations:
        try:
            raw_migration_id = int(raw_migration)
        except ValueError:
            raw_migration_id = None
        if raw_migration_id:
            migrations.append(get_migration_by_id(raw_migration_id))
        else:
            migrations.append(get_migration_by_name(raw_migration))
    return migrations


def apply_migrations(raw_migrations: list[str]):
    """Apply a series of migrations to the database."""
    try:
        migrations = parse_migrations(raw_migrations)
    except ValueError as error:
        print(error)
        sys.exit(1)
    for migration in migrations:
        print('Applying migration', migration, end='... ')
        module = importlib.import_module('.' + migration, 'migrations')
        module.apply(migrator)
        print('Done')
    print('All migrations successful.')


parser = argparse.ArgumentParser(
    description='Run specified migrations.', prog='migrations'
)
parser.add_argument('migrations', nargs='*', help='The migrations to apply.')
parser.add_argument(
    '-l', '--list', action='store_true',
    help='show a list of available migrations and exit'
)
args = parser.parse_args()

if args.list:
    display_migrations()
else:
    apply_migrations(args.migrations)
