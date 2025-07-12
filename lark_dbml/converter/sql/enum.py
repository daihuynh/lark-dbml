from sqlglot import expressions as exp

from ...schema import Enum
from .base import BaseSQLConverter


class EnumConverter(BaseSQLConverter[Enum]):
    def convert(self, node):
        enum = node
        enum_name = enum.name if not enum.db_schema else f"{enum.db_schema}.{enum.name}"
        values = ",".join(f"'{value.value}'" for value in enum.values)
        return exp.Command(
            this="CREATE", expression=f"TYPE {enum_name} AS ENUM ({values})"
        )
