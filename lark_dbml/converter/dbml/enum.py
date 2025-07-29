import os

from ...schema import Enum, EnumValueSettings
from .base import BaseDBMLConverter
from .utils import quote_identifier, quote_value, name_to_str


class EnumConverter(BaseDBMLConverter[Enum]):
    """
    DBML converter for Enum objects.

    Converts DBML Enum objects to DBML string definitions, including enum values
    and their associated settings.
    """

    def convert(self, node):
        """
        Convert a DBML Enum object to a DBML string definition.

        Args:
            node: The Enum object to convert.

        Returns:
            str: The DBML string representation of the enum.
        """
        enum = node
        enum_def = f"Enum {name_to_str(enum)} {{"
        enum_def += os.linesep
        for value in enum.values:
            enum_def += self.settings.indent + quote_identifier(value.value)
            if value.settings:
                enum_def += f" [{self._convert_value_settings(value.settings)}]"
            enum_def += os.linesep
        enum_def += "}"
        return enum_def

    def _convert_value_settings(self, settings: EnumValueSettings) -> str:
        """
        Convert enum value settings to a DBML settings string.

        Args:
            settings: The EnumValueSettings object containing settings and extra fields.

        Returns:
            str: The DBML string representation of the settings.
        """
        kv = {}
        for field in EnumValueSettings.model_fields:
            if (value := getattr(settings, field)) is not None:
                kv[field] = quote_value(value) if field == "note" else value
        if self.settings.allow_extra:
            for k, v in settings.model_extra.items():
                kv[k] = quote_value(v)
        return ", ".join(f"{k}: {v}" for k, v in kv.items())
