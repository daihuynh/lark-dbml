from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ...schema import (
    Project,
    Reference,
    TablePartial,
    Table,
    Column,
    Index,
    Enum,
    Note,
    TableGroup,
)

TableType = TypeVar("TableType", Table, TablePartial)
DBMLNode = TypeVar(
    "DBMLNode",
    Project,
    Enum,
    TableType,
    Column,
    Index,
    Reference,
    TableGroup,
    Note,
)


class DBMLConverterSettings:
    def __init__(
        self,
        indent: str = " " * 4,  # 4 spaces,
        allow_extra: bool = False,
    ):
        self.indent = indent
        self.allow_extra = allow_extra


class BaseDBMLConverter(Generic[DBMLNode], ABC):
    def __init__(self, settings: DBMLConverterSettings):
        if not settings:
            settings = DBMLConverterSettings()
        self.settings = settings

    @abstractmethod
    def convert(self, node: DBMLNode) -> str:
        raise NotImplementedError("conver function is not implemented")
