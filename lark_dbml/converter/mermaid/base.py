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


class MermaidConverterSettings:
    """
    Settings for Mermaid converters.

    Attributes:
        indent (str): String used for indentation (default: 4 spaces).
    """

    def __init__(
        self,
        indent: str = " " * 4,
    ):
        """
        Initialize MermaidConverterSettings.

        Args:
            indent: String used for indentation.
        """
        self.indent = indent


class BaseMermaidConverter(Generic[DBMLNode], ABC):
    """
    Abstract base class for Mermaid converters.
    """

    def __init__(self, settings: MermaidConverterSettings):
        """
        Initialize the converter with Mermaid converter settings.

        Args:
            settings: MermaidConverterSettings object.
        """
        if not settings:
            settings = MermaidConverterSettings()
        self.settings = settings

    @abstractmethod
    def convert(self, node: DBMLNode) -> str:
        """
        Convert a DBML schema node to a Mermaid string representation.

        Args:
            node: The DBML schema node to convert.

        Returns:
            str: The Mermaid string representation of the node.
        """
        raise NotImplementedError("convert function is not implemented")
