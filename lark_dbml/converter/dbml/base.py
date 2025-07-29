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
    """
    Settings for DBML converters.

    Attributes:
        indent (str): String used for indentation (default: 4 spaces).
        allow_extra (bool): Whether to allow extra fields in output (default: False).
    """

    def __init__(
        self,
        indent: str = " " * 4,  # 4 spaces,
        allow_extra: bool = False,
    ):
        """
        Initialize DBMLConverterSettings.

        Args:
            indent: String used for indentation.
            allow_extra: Whether to allow extra fields in output.
        """
        self.indent = indent
        self.allow_extra = allow_extra


class BaseDBMLConverter(Generic[DBMLNode], ABC):
    """
    Abstract base class for DBML converters.

    Subclasses should implement the convert method to transform a DBML schema node
    into a DBML string representation using the provided settings.
    """

    def __init__(self, settings: DBMLConverterSettings):
        """
        Initialize the converter with DBML converter settings.

        Args:
            settings: DBMLConverterSettings object.
        """
        if not settings:
            settings = DBMLConverterSettings()
        self.settings = settings

    @abstractmethod
    def convert(self, node: DBMLNode) -> str:
        """
        Convert a DBML schema node to a DBML string representation.

        Args:
            node: The DBML schema node to convert.

        Returns:
            str: The DBML string representation of the node.
        """
        raise NotImplementedError("convert function is not implemented")
