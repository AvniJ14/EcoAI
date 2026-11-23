
from sqlalchemy import inspect

from app.database.database import Base, engine

# Import models so SQLAlchemy registers all tables and columns.
from app.models.benchmark import (
    BenchmarkRun,
    ModelResult,
    ExperimentMetric
)


def migrate_existing_tables():
    """
    Add columns introduced in newer model versions.

    Existing tables and records are preserved.
    Missing columns are added without deleting existing data.
    """

    print("\nChecking existing database schema...")

    inspector = inspect(engine)

    with engine.begin() as connection:

        for table in Base.metadata.sorted_tables:

            table_name = table.name

            # Skip tables that do not exist yet.
            if not inspector.has_table(table_name):
                continue

            existing_columns = {
                column["name"]
                for column in inspect(connection).get_columns(table_name)
            }

            for column in table.columns:

                if column.name in existing_columns:
                    continue

                column_type = column.type.compile(
                    dialect=engine.dialect
                )

                quoted_table = engine.dialect.identifier_preparer.quote(
                    table_name
                )

                quoted_column = engine.dialect.identifier_preparer.quote(
                    column.name
                )

                # Add the missing column as nullable so existing
                # records remain valid and are not deleted.
                sql = (
                    f"ALTER TABLE {quoted_table} "
                    f"ADD COLUMN {quoted_column} {column_type}"
                )

                connection.exec_driver_sql(sql)

                print(
                    f"Added column '{column.name}' "
                    f"to table '{table_name}'"
                )

    print("Database migration completed.")


def initialize_database():

    print("Initializing EcoAI database...")

    # Create tables that do not already exist.
    Base.metadata.create_all(bind=engine)

    # Add new columns to existing tables.
    migrate_existing_tables()

    print("\nDatabase initialized successfully!")
    print(f"Database location: {engine.url.database}")

    print("\nUpdated database schema:")

    inspector = inspect(engine)

    for table in Base.metadata.sorted_tables:

        print(f"\nTable: {table.name}")

        columns = inspector.get_columns(table.name)

        for column in columns:
            print(f"  - {column['name']}")


if __name__ == "__main__":
    initialize_database()
