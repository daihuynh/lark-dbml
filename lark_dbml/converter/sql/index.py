from sqlglot import Dialects, expressions as exp

from ...schema import Index, Table
from .base import BaseSQLConverter


class IndexConverter(BaseSQLConverter[Index]):
    """
    SQL converter for DBML Index objects.

    Converts DBML index definitions to SQLGlot index expressions,
    including support for dialect-specific features like NULLS FIRST.
    """

    def __init__(self, dialect, table: Table):
        """
        Initialize the index converter.

        Args:
            dialect: The SQL dialect to use for conversion.
            table: The Table object associated with the index.
        """
        super().__init__(dialect)
        self.table = table

    @property
    def support_nulls_first(self) -> bool:
        """
        Indicates if the dialect supports NULLS FIRST in index ordering.

        Returns:
            bool: True if NULLS FIRST is supported, False otherwise.
        """
        return self.dialect in [
            Dialects.POSTGRES,
            Dialects.ORACLE,
            Dialects.DUCKDB,
        ]

    def convert(self, node):
        """
        Convert a DBML Index object to a SQLGlot index creation expression.

        Args:
            node: The Index object to convert.

        Returns:
            exp.Create: The SQLGlot index creation expression.
        """
        index = node
        columns = []
        for column in index.columns:
            is_func_exp = "`" in column
            name = f"({column.strip('`')})" if is_func_exp else column
            columns.append(
                exp.Ordered(
                    this=exp.Column(
                        this=exp.Identifier(this=name, quoted=not is_func_exp)
                    ),
                    nulls_first=not self.support_nulls_first,
                )
            )

        index_ref = exp.Create(
            this=exp.Index(
                this=exp.Identifier(this=index.settings.name, quoted=True)
                if index.settings and index.settings.name
                else None,
                table=exp.Table(
                    this=exp.Identifier(this=self.table.name, quoted=True),
                    db=exp.Identifier(this=self.table.db_schema, quoted=True)
                    if self.table.db_schema
                    else None,
                ),
                params=exp.IndexParameters(
                    columns=columns,
                    using=exp.Var(this=index.settings.idx_type.upper())
                    if index.settings and index.settings.idx_type
                    else None,
                ),
            ),
            kind="INDEX",
            unique=index.settings and index.settings.is_unique,
        )
        return index_ref


class CompositePKIndexConverter(BaseSQLConverter[Index]):
    """
    SQL converter for composite primary key indexes.

    Converts DBML composite primary key definitions to SQLGlot PRIMARY KEY expressions.
    """

    def convert(self, node):
        """
        Convert a DBML Index object representing a composite primary key
        to a SQLGlot PRIMARY KEY expression.

        Args:
            node: The Index object to convert.

        Returns:
            exp.PrimaryKey: The SQLGlot PRIMARY KEY expression.
        """
        index = node
        return exp.PrimaryKey(
            expressions=list(
                map(
                    lambda column: exp.Identifier(this=column, quoted=True),
                    index.columns,
                )
            )
        )
