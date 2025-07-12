from io import StringIO
import os
from sqlglot import Dialects, expressions as exp

from ...schema import Diagram
from .enum import EnumConverter
from .index import IndexConverter
from .table import TableConverter


def to_sql(diagram: Diagram, dialect: Dialects = Dialects.POSTGRES):
    endblock = ";" + os.linesep + os.linesep

    enum_converter = EnumConverter(dialect)
    with StringIO() as buffer:
        # Create schema
        schemas = set(
            map(
                lambda enum: enum.db_schema,
                filter(lambda enum: enum.db_schema is not None, diagram.enums),
            )
        )
        schemas |= set(
            map(
                lambda table: table.db_schema,
                filter(lambda table: table.db_schema is not None, diagram.tables),
            )
        )
        for schema in sorted(schemas):
            schema_def = exp.Create(
                this=exp.Table(db=exp.Identifier(this=schema, quoted=True)),
                kind="SCHEMA",
                exists=True,
            )
            buffer.write(schema_def.sql(dialect=dialect, pretty=True))
            buffer.write(endblock)

        # Only create enum if the dialect supports
        if dialect in [Dialects.POSTGRES, Dialects.DUCKDB]:
            # Create enum
            if diagram.enums:
                for enum in diagram.enums:
                    enum_def = enum_converter.convert(enum)
                    buffer.write(enum_def.sql(dialect, pretty=True))
                    buffer.write(endblock)

        # Create Table along with Indexes
        for table in diagram.tables:
            # Find any references of this table
            references = list(
                filter(
                    lambda ref: ref.from_table.db_schema == table.db_schema
                    and ref.from_table.name == table.name,
                    diagram.references,
                )
            )

            table_converter = TableConverter(
                dialect,
                table_partials=diagram.table_partials,
                references=references,
                enums=diagram.enums,
            )
            index_converter = IndexConverter(dialect, table)

            table_def = table_converter.convert(table)
            buffer.write(table_def.sql(dialect=dialect, pretty=True))
            buffer.write(endblock)

            if table.indexes:
                # Indexes that are not composite primary keys
                indexes = list(
                    filter(
                        lambda index: not (
                            index.settings and index.settings.is_primary_key
                        ),
                        table.indexes,
                    )
                )
                for index in indexes:
                    index_def = index_converter.convert(index)
                    buffer.write(index_def.sql(dialect=dialect, pretty=True))
                    buffer.write(endblock)

        return buffer.getvalue()
