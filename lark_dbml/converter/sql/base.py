from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from sqlglot import Dialects, expressions as exp

from ...schema import Reference, Table, Column, Index, Enum


DBMLNode = TypeVar("DBMLNode", Table, Column, Index, Enum, Reference)


class BaseSQLConverter(Generic[DBMLNode], ABC):
    def __init__(self, dialect: Dialects):
        self.dialect = dialect

    @abstractmethod
    def convert(self, node: DBMLNode) -> exp.Expression:
        raise NotImplementedError("conver function is not implemented")
