[![](https://img.shields.io/pypi/v/lark-dbml.svg)](https://pypi.org/project/lark-dbml/)
[![](https://img.shields.io/github/v/tag/daihuynh/lark-dbml.svg?label=GitHub)](https://github.com/daihuynh/lark-dbml)
[![codecov](https://codecov.io/gh/daihuynh/lark-dbml/graph/badge.svg?token=YZPWVIS3QA)](https://codecov.io/gh/daihuynh/lark-dbml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI Downloads](https://static.pepy.tech/badge/lark-dbml)](https://pepy.tech/projects/lark-dbml)


# Lark-DBML

* [Features](#features)
* [Milestones](#milestones)
* [Installation](#installation)
* [Usage](#usage)
  * [Output Structure](#output-structure)
  * [Parser](#parser)
    * [Load](#load-dbml)
    * [Dump](#dump-dbml)
  * [Converters](#converters)
    * [SQL](#sql)
    * [Data Contract](#data-contract)
* [Development](#development)
* [License](#license)

A Python parser for [Database Markup Language (DBML)](https://dbml.dbdiagram.io) built with the powerful LARK parsing toolkit, utilizing the Earley algorithm for robust and flexible parsing.

## Features

* **DBML Parsing:** Accurately parses DBML files using an EBNF grammar defined for Lark.
* **Earley Parser:** Utilizes Lark's Earley parser for efficient and flexible parsing.
* **Pydantic Validation:** Ensures the parsed DBML data conforms to a well-defined structure using Pydantic 2.11, providing reliable data integrity.
* **Structured Output:** Generates Python objects representing your DBML diagram, making it easy to programmatically access and manipulate your database schema.
* **Future-Proof:** the parser accepts any properties or settings that are not defined in the DBML spec.
* **Support multiple converters**:
  * **SQL**: convert Pydantic output model to SQL with SQLGlot.
  * **DBML**: convert Pydantic model to DBML.

## Milestones

- [x] DBML Parser - Earley
- [x] SQL Converter
- [x] DBML Converter
- [x] Data Contract Converter
- [ ] Generate DBML from a database connection string
- [ ] Optimised DBML Parser - LALR(1)
- [ ] CLI

## Installation

You can install lark-dbml using pip:

```bash
pip install lark-dbml
```

To use SQL converter
```bash
pip install "lark-dbml[sql]"
```

## Usage

### Output Structure

Diagram - a Pydantic model - defines the expected structure of the parsed DBML content, ensuring consistency and type safety.

```python
class Diagram(BaseModel):
    project: Project
    enums: list[Enum] | None = []
    table_groups: list[TableGroup] | None = []
    sticky_notes: list[Note] | None = []
    references: list[Reference] | None = []
    tables: list[Table] | None = []
    table_partials : list[TablePartial] | None = []
```

### Parser

lark-dbml uses the same API as other parser packages in Python.

#### Load DBML

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

The parser can read any settings or properties in DBML objects even if the spec doesn't define them.

```python
diagram = loads("""
Table myTable [newkey: 'random_value'] {
    id int [pk]
}
""")
```

```
>>> diagram.tables[0].settings
TableSettings(note=None, header_color=None, newkey='random_value')
```

#### Dump DBML


```python
from lark_dbml import dump, dumps

from lark_dbml.converter.dbml import DBMLConverterSettings
from lark_dbml.schema import (
    Column,
    ColumnSettings,
    DataType,
    Diagram,
    Table,
    TableSettings
)

diagram = Diagram(
    tables=[
        Table(
            name="body",
            alias="full_table",
            note="Incorporated with header and footer",
            settings=TableSettings(
                headercolor="#3498DB",
                note="header note",
                partitioned_by="id"
            ),
            columns=[
                Column(
                    name="id",
                    data_type=DataType(sql_type="int"),
                    settings=ColumnSettings(
                        is_primary_key=True, note="why is id behind name?"
                    ),
                ),
                Column(
                    name="audit_date",
                    data_type=DataType(sql_type="timestamp"),
                    settings=ColumnSettings(default="`getdate()`"),
                ),
            ],
        )
    ]
)

# This converts the diagram to DBML,
# but partitioned_by will not be included
dumps(diagram)

# This includes partitioned_by in the output
dumps(diagram,
      settings=DBMLConverterSettings(
          allow_extra=True
      )
)

# Write the DBML to file
dump(diagram, 'diagram.dbml')
```

### Converters

#### SQL

SQL conversion is backed by **sqlglot** package. The underlying code converts the output Pydantic model to **sqlglot**'s AST Expression. Using **sqlglot** helps transpilation to any SQL dialect easily.

**NOTE THAT**: the output SQL is not guaranteed to be perfect or completely functional due to differences between dialects. If you find any issue, please create a new issue in Github :)

```python
from lark_dbml import load
from lark_dbml.converter import to_sql
from sqlglot import Dialects

# Load DBML diagram
diagram = load("diagram.dbml")

# Convert to SQL for PostgreSQL
sql = to_sql(diagram, Dialects.POSTGRES)
```

#### Data Contract

Convert DBML diagram to a [Data Contract](https://datacontract.com) spec file. The basic usage just convert tables and columns to "model" and "definition" sections. However, `lark-dbml` supports settings to extract more information from a DBML - please expand Advanced Usage.

<details>
<summary>Basic example</summary>

```python
from lark_dbml import load
from lark_dbml.converter import to_data_contract

# Load DBML diagram
diagram = load("diagram.dbml")

# Convert to SQL for PostgreSQL
data_contract = to_data_contract(diagram)
```

</details>

<details>
<summary>Advanced Usage</summary>

You can leverage Sticky Notes in DBML to store information about "terms" and "servers" in JSON or YAML format. Then, you can set `note_as_fields` in the settings to parse and include those information in the generated contract. Here is the example

```python
import json
from lark_dbml import load
from lark_dbml.converter import to_data_contract
from lark_dbml.converter.datacontract import DataContractConverterSettings

# complex_datacontract.dbml inside the exmaples folder in this repo
diagram = load('examples/complex_datacontract.dbml')

# project_as_info: properties in Project are put into "info"
# note_as_description: note in Table Settings is treated as model description.
# note_as_fields: inline note in Table is parsed and extends the corresponding model's properties.
# deserialization_func is required once note_as_fields is set. This is the function to parse the content inside an inline note. In this example, it's JSON

data_contract = to_data_contract(diagram=diagram,
                       settings=DataContractConverterSettings(
                        project_as_info=True,
                        note_as_description=True,
                        note_as_fields=True,
                        deserialization_func=json.loads
                       ))
```

</details>

## Development

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
