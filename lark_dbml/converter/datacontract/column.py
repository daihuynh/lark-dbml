from ...schema import Column, DataType
from .base import BaseDataContractConverter


class ColumnConverter(BaseDataContractConverter[Column]):
    """
    Data contract converter for Column objects.

    Converts DBML Column objects to data contract dictionary definitions, including data type,
    settings, flags, and inline references.
    """

    def convert(self, node):
        """
        Convert a DBML Column object to a data contract dictionary definition.

        Args:
            node: The Column object to convert.

        Returns:
            dict: The data contract dictionary representation of the column.
        """
        column = node
        is_data_type = isinstance(column.data_type, DataType)
        kv = {
            "fields": {
                column.name: {
                    "$ref": f"#/definitions/{column.name}",
                }
            },
            "definitions": {
                column.name: {
                    "type": column.data_type.sql_type if is_data_type else "string"
                }
            },
        }
        if is_data_type:
            if column.data_type.length and column.data_type.scale:
                kv["definitions"][column.name]["precision"] = column.data_type.length
                kv["definitions"][column.name]["scale"] = column.data_type.scale
            elif column.data_type.length:
                kv["definitions"][column.name]["maxLength"] = column.data_type.length

        settings = column.settings
        if settings:
            if settings.note:
                if self.settings.note_as_fields:
                    props = self.settings.deserialization_func(settings.note)
                    kv["definitions"][column.name].update(props)
                elif self.settings.note_as_description:
                    kv["definitions"][column.name]["description"] = settings.note
            if settings.is_primary_key:
                kv["fields"][column.name]["primaryKey"] = True
            if settings.is_null is False:
                kv["fields"][column.name]["required"] = True
            if settings.is_unique:
                kv["fields"][column.name]["unique"] = True
            if settings.default:
                kv["fields"][column.name]["examples"] = [settings.default]
            if settings.ref:
                kv["fields"][column.name]["references"] = (
                    f"{settings.ref.to_table.name}.{settings.ref.to_columns[0]}"
                )

        return kv
