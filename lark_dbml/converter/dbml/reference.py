from ...schema import Name, Reference, ReferenceSettings
from .base import BaseDBMLConverter
from .utils import quote_identifier, quote_value, name_to_str


class ReferenceConverter(BaseDBMLConverter[Reference]):
    """
    DBML converter for Reference objects.

    Converts DBML Reference objects to DBML string definitions, including columns,
    relationships, and settings.
    """

    def convert(self, node):
        """
        Convert a DBML Reference object to a DBML string definition.

        Args:
            node: The Reference object to convert.

        Returns:
            str: The DBML string representation of the reference.
        """
        reference = node
        if reference.name:
            reference_def = f"Ref {name_to_str(reference)}: "
        else:
            reference_def = "Ref: "
        if len(reference.from_columns) == 1:
            reference_def += (
                f"{name_to_str(reference.from_table)}"
                "."
                f"{quote_identifier(reference.from_columns[0])}"
                f" {reference.relationship} "
                f"{name_to_str(reference.to_table)}"
                "."
                f"{quote_identifier(reference.to_columns[0])}"
            )
        else:
            reference_def += (
                f"{name_to_str(reference.from_table)}"
                ".("
                f"{','.join(quote_identifier(column) for column in reference.from_columns)}"
                ")"
                f" {reference.relationship} "
                f"{name_to_str(reference.to_table)}"
                ".("
                f"{','.join(quote_identifier(column) for column in reference.to_columns)}"
                ")"
            )
        if reference.settings:
            settings_def = self._convert_settings(reference.settings)
            if settings_def:
                reference_def += f" [{settings_def}]"
        return reference_def

    def _convert_settings(self, settings: ReferenceSettings) -> str:
        """
        Convert reference settings to a DBML settings string.

        Args:
            settings: The ReferenceSettings object containing settings and extra fields.

        Returns:
            str: The DBML string representation of the settings.
        """
        kv = {}
        for field in ReferenceSettings.model_fields:
            if field not in Name.model_fields:
                if (value := getattr(settings, field)) is not None:
                    kv[field] = value
        if self.settings.allow_extra:
            for k, v in settings.model_extra.items():
                kv[k] = quote_value(v)

        return ", ".join(f"{k}: {v}" for k, v in sorted(kv.items()))
