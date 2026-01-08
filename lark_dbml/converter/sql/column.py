from typing import List
from sqlglot import Dialects, expressions as exp
from .base import BaseSQLConverter
from ...schema import Column, ColumnSettings, DataType, Enum


class ColumnConverter(BaseSQLConverter[Column]):
    """
    SQL converter for DBML Column objects.

    Converts DBML column definitions to SQLGlot column expressions,
    including data types, constraints, defaults, and references.
    """

    def __init__(self, dialect, enums: List[Enum]):
        """
        Initialize the column converter.

        Args:
            dialect: The SQL dialect to use for conversion.
            enums: List of Enum objects for type resolution.
        """
        super().__init__(dialect)
        self.enums = enums

    @property
    def support_inline_enum_def(self) -> bool:
        """
        Indicates if the dialect supports inline enum definitions.

        Returns:
            bool: True if inline enum definitions are supported, False otherwise.
        """
        return self.dialect == Dialects.MYSQL

    def _convert_settings(self, settings: ColumnSettings) -> List[exp.Constraint]:
        """
        Convert DBML column settings to SQLGlot constraints.

        Args:
            settings: ColumnSettings object containing constraints and defaults.

        Returns:
            List[exp.Constraint]: List of SQLGlot constraint expressions.
        """
        constraints = []
        if settings.is_increment:
            constraints.append(
                exp.ColumnConstraint(
                    kind=exp.GeneratedAsIdentityColumnConstraint(this=True)
                )
            )
        if settings.is_unique:
            constraints.append(exp.ColumnConstraint(kind=exp.UniqueColumnConstraint()))
        if settings.is_primary_key:
            constraints.append(
                exp.ColumnConstraint(kind=exp.PrimaryKeyColumnConstraint())
            )
        # Only set NULL or NOT NULL if the column is not a primary key
        if settings.is_null is not None:
            constraints.append(
                exp.ColumnConstraint(
                    kind=exp.NotNullColumnConstraint(allow_null=settings.is_null)
                )
            )
        # Default value
        if settings.default is not None:
            is_func_exp = isinstance(settings.default, str) and "`" in settings.default
            default_value = (
                settings.default if not is_func_exp else settings.default.strip("`")
            )
            is_string_literal = isinstance(default_value, str) and not is_func_exp
            constraints.append(
                exp.ColumnConstraint(
                    kind=exp.DefaultColumnConstraint(
                        this=exp.Literal(
                            this=default_value
                            if is_string_literal
                            else str(default_value),
                            is_string=is_string_literal,
                        )
                    )
                )
            )
        # Checks:
        if settings.checks:
            for check in settings.checks:
                constraints.append(
                    exp.ColumnConstraint(
                        kind=exp.CheckColumnConstraint(
                            this=exp.Literal(
                                this=check.strip("`"),
                                is_string=False,
                            )
                        )
                    )
                )
        # Reference
        if settings.ref:
            constraints.append(
                exp.ColumnConstraint(
                    kind=exp.Reference(
                        this=exp.Schema(
                            this=exp.Table(
                                this=exp.Identifier(
                                    this=settings.ref.to_table.name, quoted=True
                                ),
                                db=exp.Identifier(
                                    this=settings.ref.to_table.db_schema, quoted=True
                                )
                                if settings.ref.to_table.db_schema
                                else None,
                            ),
                            expressions=[
                                exp.Identifier(
                                    this=settings.ref.to_columns[0], quoted=True
                                )
                            ],
                        )
                    )
                )
            )
        return constraints

    def convert(self, node):
        """
        Convert a DBML Column object to a SQLGlot column definition.

        Args:
            node: The Column object to convert.

        Returns:
            exp.ColumnDef: The SQLGlot column definition expression.
        """
        column = node

        data_type: exp.DataType.Type = exp.DataType.Type.UNKNOWN
        enum: Enum = None
        if isinstance(column.data_type, DataType):
            type_name = column.data_type.sql_type
        else:
            type_name = f"{column.data_type.db_schema}.{column.data_type.name}"

        try:
            data_type = exp.DataType.Type(type_name.upper())
        except Exception:
            for e in self.enums:
                enum_name = e.name if not e.db_schema else f"{e.db_schema}.{e.name}"
                if type_name == enum_name:
                    enum = e
                    data_type = exp.DataType.Type.ENUM
                    break
            else:
                data_type = exp.DataType.Type.USERDEFINED

        if data_type == exp.DataType.Type.ENUM and not self.support_inline_enum_def:
            data_type = exp.DataType.Type.USERDEFINED

        match data_type:
            case exp.DataType.Type.ENUM:
                kind = exp.DataType(
                    this=data_type,
                    nested=False,
                    expressions=list(
                        map(
                            lambda value: exp.Literal(this=value.value, is_string=True),
                            enum.values,
                        )
                    ),
                )
            case exp.DataType.Type.USERDEFINED:
                kind = exp.DataType(
                    this=data_type,
                    nested=False,
                    kind=(type_name if " " not in type_name else f'"{type_name}"'),
                )
            case _:
                expressions = []
                if column.data_type.length:
                    expressions.append(
                        exp.DataTypeParam(
                            this=exp.Literal(
                                this=column.data_type.length, is_string=False
                            )
                        )
                    )
                if column.data_type.scale:
                    expressions.append(
                        exp.DataTypeParam(
                            this=exp.Literal(
                                this=column.data_type.scale, is_string=False
                            )
                        )
                    )
                kind = exp.DataType(
                    this=data_type, nested=False, expressions=expressions
                )

        col_def = exp.ColumnDef(
            this=exp.Identifier(this=column.name, quoted=True), kind=kind
        )

        if column.settings:
            col_def.set("constraints", self._convert_settings(column.settings))
        return col_def
