# Lark-DBML Context for AI Agents

## Project Overview
`lark-dbml` is a Python parser for [DBML (Database Markup Language)](https://dbml.dbdiagram.io) built with the LARK parsing toolkit. It provides both parsing (DBML -> Python objects) and conversion capabilities (DBML -> SQL, SQL -> DBML, DBML -> Mermaid).

## Core Components
- **Parser**: Uses `lark` (Earley/LALR) to parse DBML into Pydantic models (`lark_dbml.schema`).
- **Schema**: Pydantic models in `lark_dbml/schema.py` define the internal representation (Diagram, Table, Column, etc.).
- **Converters**:
  - **SQL**: `lark_dbml/converter/sql/` (uses `sqlglot` for robust SQL handling). Handles both `to_sql` (DBML -> SQL) and `from_sql` (SQL -> DBML).
  - **Mermaid**: `lark_dbml/converter/mermaid/` (DBML -> Mermaid ERD).
  - **Data Contract**: `lark_dbml/converter/datacontract/`.
  - **DBML**: `lark_dbml/converter/dbml/` (Model -> DBML string).

## Key Features
- **Round-Trip Parsing**: Pydantic models <-> DBML string.
- **SQL Round-Trip**: SQL DDL <-> DBML (via `lark_dbml.converter.from_sql` and `to_sql`).
- **Standalone Mode**: Can generate a standalone parser without external grammar files.

## Testing
- Tests are located in `tests/`.
- `tests/expectation/` contains SQL and DBML files for data-driven testing.
- Use `uv run pytest` to run tests.

## Versioning
- This project follows semantic versioning.
- Version is typically managed in `pyproject.toml` or `__init__.py`.

## Environment Setup

This project uses `uv` for dependency management.

1.  **Install `uv`**:
    ```bash
    pip install uv
    ```

2.  **Install Dependencies**:
    ```bash
    uv sync --all-groups
    ```

3.  **Run Tests**:
    ```bash
    uv run pytest
    ```

4.  **Run Coverage**:
    ```bash
    uv run coverage run -m pytest
    uv run coverage report
    ```
