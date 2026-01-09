from ...schema import ColumnSettings, Column, Name, ReferenceInline
from .base import BaseDBMLConverter
from .utils import name_to_str, quote_identifier, quote_value


class ColumnConverter(BaseDBMLConverter[Column]):
    """
    DBML converter for Column objects.

    Converts DBML Column objects to DBML string definitions, including data type,
    settings, flags, and inline references.
    """

    def convert(self, node):
        """
        Convert a DBML Column object to a DBML string definition.

        Args:
            node: The Column object to convert.

        Returns:
            str: The DBML string representation of the column.
        """
        column = node
        column_def = self.settings.indent
        column_def += quote_identifier(column.name)
        if isinstance(column.data_type, Name):
            column_def += f" {name_to_str(column.data_type)}"
        else:
            column_def += f" {quote_identifier(column.data_type.sql_type)}"
            if column.data_type.length and column.data_type.scale:
                column_def += f"({column.data_type.length},{column.data_type.scale})"
            elif column.data_type.length:
                column_def += f"({column.data_type.length})"
        if column.settings:
            column_def += f" [{self._convert_index_settings(column.settings)}]"
        return column_def

    def _convert_index_settings(self, settings: ColumnSettings):
        """
        Convert column settings to a DBML settings string.

        Args:
            settings: The ColumnSettings object containing settings and flags.

        Returns:
            str: The DBML string representation of the settings.
        """
        kv = {}
        for field in ColumnSettings.model_fields:
            if (
                ColumnSettings.model_fields[field].annotation is not bool
                and ColumnSettings.model_fields[field].annotation != bool | None
                and field != "ref"
                and (value := getattr(settings, field)) is not None
            ):
                match field:
                    case "note":
                        kv[field] = quote_value(value)
                    case "default":
                        kv[field] = (
                            value
                            if not isinstance(value, str) or "`" in value
                            else f'"{value}"'
                        )
                    case _:
                        kv[field] = value
        if self.settings.allow_extra:
            for k, v in settings.model_extra.items():
                kv[k] = quote_value(v)

        flags = []
        if settings.is_primary_key:
            flags.append("pk")
        else:
            if settings.is_null is not None:
                flags.append("null" if settings.is_null else "not null")
        if settings.is_unique:
            flags.append("unique")
        if settings.is_increment:
            flags.append("increment")

        ref_def = []
        if settings.ref:
            ref_def.append(self._convert_inline_reference(settings.ref))

        kv = list(f"{k}: {v}" for k, v in sorted(kv.items()))

        return ", ".join(ref_def + flags + kv)

    def _convert_inline_reference(self, reference: ReferenceInline):
        """
        Convert an inline reference to a DBML reference string.

        Args:
            reference: The ReferenceInline object to convert.

        Returns:
            str: The DBML string representation of the inline reference.
        """
        return (
            f"ref: {reference.relationship} "
            f"{name_to_str(reference.to_table)}"
            "."
            f"{quote_identifier(reference.to_columns[0])}"
        )
