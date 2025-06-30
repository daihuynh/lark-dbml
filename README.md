[![](https://img.shields.io/pypi/v/lark-dbml.svg)](https://pypi.org/project/lark-dbml/)
[![](https://img.shields.io/github/v/tag/daihuynh/lark-dbml.svg?label=GitHub)](https://github.com/daihuynh/lark-dbml)
[![codecov](https://codecov.io/gh/daihuynh/lark-dbml/graph/badge.svg?token=YZPWVIS3QA)](https://codecov.io/gh/daihuynh/lark-dbml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


# Lark-DBML

> The parser is currently on alpha stage. It doesn't have any tests or docstrings yet.

A Python parser for [Database Markup Language (DBML)](https://dbml.dbdiagram.io) built with the powerful LARK parsing toolkit, utilizing the Earley algorithm for robust and flexible parsing.

## Features

* **DBML Parsing:** Accurately parses DBML files using an EBNF grammar defined for Lark.
* **Earley Parser:** Utilizes Lark's Earley parser for efficient and flexible parsing.
* **Pydantic Validation:** Ensures the parsed DBML data conforms to a well-defined structure using Pydantic 2.11, providing reliable data integrity.
* **Structured Output:** Generates Python objects representing your DBML diagram, making it easy to programmatically access and manipulate your database schema.

## Installation

You can install lark-dbml using pip:

```bash
pip install lark-dbml
```

## Usage

```python
from lark_dbml import load, loads

# 1. Read from a string
dbml = """
Project "My Database" {
  database_type: 'PostgreSQL'
  Note: "This is a sample database"
}

Table "users" {
  id int [pk, increment]
  username varchar [unique, not null]
  email varchar [unique]
  created_at timestamp [default: `now()`]
}

Table "posts" {
  id int [pk, increment]
  title varchar
  content text
  user_id int
}

Ref: posts.user_id > users.id
"""

diagram = loads(dbml)

# 2. Read from a file
diagram = load('example.dbml')
```

Diagrame structure
```Python
class Diagram(BaseModel):
    project: Project
    enums: list[Enum] | None = []
    table_groups: list[TableGroup] | None = []
    sticky_notes: list[Note] | None = []
    references: list[Reference] | None = []
    tables: list[Table] | None = []
    table_partials : list[TablePartial] | None = []
```

## Output Structure

Diagram - a Pydantic model - defines the expected structure of the parsed DBML content, ensuring consistency and type safety.

```python
class Diagram(BaseModel):
    project: Project
    enums: Optional[List[Enum]] = []
    table_groups: Optional[List[TableGroup]] = []
    sticky_notes: Optional[List[Note]] = []
    references: Optional[List[Reference]] = []
    tables: Optional[List[Table]] = []
    table_partials : Optional[List[TablePartial]] = []
```

## Development

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
