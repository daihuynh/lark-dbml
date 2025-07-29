from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from ...schema import (
    Project,
    Reference,
    TablePartial,
    Table,
    Column,
    Enum,
    Note,
)

DeserializationFunc = Callable[[str], Any]

TableType = TypeVar("TableType", Table, TablePartial)
DBMLNode = TypeVar(
    "DBMLNode",
    Project,
    Enum,
    TableType,
    Column,
    Reference,
    Note,
)


class DataContractConverterSettings:
    """
    Settings for Data Contract converters.
    """

    def __init__(
        self,
        project_as_info=False,
        note_as_description=False,
        note_as_fields=False,
        deserialization_func: DeserializationFunc = None,  # must set when note_as_fields is True
    ):
        """
        Initialize DataContractConverterSettings.

        Args:
            project_as_info: Whether to treat the project as the info section.
            note_as_description: Whether to use notes as descriptions.
            note_as_fields: Whether to parse notes as fields.
            deserialization_func: Function to deserialize note fields if note_as_fields is True.
        """
        self.project_as_info = project_as_info
        self.note_as_description = note_as_description
        self.note_as_fields = note_as_fields
        self.deserialization_func = deserialization_func


class BaseDataContractConverter(Generic[DBMLNode], ABC):
    """
    Abstract base class for Data Contract converters.

    Subclasses should implement the convert method to transform a Contract schema node
    into a Contract dictionary representation using the provided settings.
    """

    def __init__(self, settings: DataContractConverterSettings):
        """
        Initialize the converter with DataContractConverterSettings.

        Args:
            settings: DataContractConverterSettings object.
        """
        if not settings:
            settings = DataContractConverterSettings()
        self.settings = settings

    @abstractmethod
    def convert(self, node: DBMLNode) -> dict[str, Any]:
        """
        Convert a Contract schema node to a Contract dictionary representation.

        Args:
            node: The Contract schema node to convert.

        Returns:
            dict[str, Any]: The Contract dictionary representation of the node.
        """
        raise NotImplementedError("convert function is not implemented")
