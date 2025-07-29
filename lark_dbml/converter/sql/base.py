from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from sqlglot import Dialects, expressions as exp

from ...schema import Reference, Table, Column, Index, Enum

DBMLNode = TypeVar("DBMLNode", Table, Column, Index, Enum, Reference)


class BaseSQLConverter(Generic[DBMLNode], ABC):
    """
    Abstract base class for SQL converters.

    Subclasses should implement the convert method to transform a DBML schema node
    into a SQLGlot expression for the specified dialect.
    """

    def __init__(self, dialect: Dialects):
        """
        Initialize the converter with a SQL dialect.

        Args:
            dialect: The SQL dialect to use for conversion.
        """
        self.dialect = dialect

    @abstractmethod
    def convert(self, node: DBMLNode) -> exp.Expression:
        """
        Convert a DBML schema node to a SQLGlot expression.

        Args:
            node: The DBML schema node to convert.

        Returns:
            exp.Expression: The resulting SQLGlot expression.
        """
        raise NotImplementedError
