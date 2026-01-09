from typing import Any, Annotated, Dict, Literal, List
from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from pydantic.aliases import AliasChoices


class Settings(BaseModel):
    """
    Base settings model that allows extra fields.
    """

    model_config = ConfigDict(extra="allow")


class Noteable(BaseModel):
    """
    Mixin for models that can have a note field.
    """

    note: str | None = Field(
        default=None, validation_alias=AliasChoices("note", "Note")
    )


class Name(BaseModel):
    """
    Base model for named schema objects, with database schema and name.
    """

    db_schema: str | None = None
    name: str | None = None

    def __str__(self):
        return f"{self.db_schema}.{self.name}" if self.db_schema else self.name


# Project
class Project(Name, Noteable):
    """
    Represents a DBML project with optional database type.
    """

    model_config = ConfigDict(extra="allow")
    database_type: str | None = None


# TableGroup
class TableGroup(Name, Noteable):
    """
    Represents a group of tables with optional settings.
    """

    tables: List[Name]
    settings: Settings | None = None


# Enum
class EnumValueSettings(Settings, Noteable):
    """
    Settings for individual enum values, supporting notes.
    """

    pass


class EnumValue(BaseModel):
    """
    Represents a single value in an enum, with optional settings.
    """

    value: str
    settings: EnumValueSettings | None = None


class Enum(Name):
    """
    Represents an enum type with a list of possible values.
    """

    values: List[EnumValue]


# Sticky Note
class Note(Name, Noteable):
    """
    Represents a sticky note in the diagram.
    """

    pass


# Relationship
class ReferenceInline(BaseModel):
    """
    Represents an inline reference between tables, including relationship type and target columns.
    """

    relationship: Literal["-", ">", "<", "<>"]
    to_table: Name
    to_columns: Annotated[
        List[str], BeforeValidator(lambda v: v if not v or isinstance(v, List) else [v])
    ] = None


class ReferenceSettings(Settings):
    """
    Settings for a reference, including delete/update actions and color.
    """

    delete: (
        Literal["cascade", "restrict", "set null", "set default", "no action"] | None
    ) = None
    update: (
        Literal["cascade", "restrict", "set null", "set default", "no action"] | None
    ) = None
    color: str | None = None  # For rendering


class Reference(Name, ReferenceInline):
    """
    Represents a reference between tables, including settings and source/target columns.
    """

    settings: ReferenceSettings | None = None
    from_table: Name | None = None
    from_columns: Annotated[
        List[str], BeforeValidator(lambda v: v if not v or isinstance(v, List) else [v])
    ] = None


# Table
class DataType(BaseModel):
    """
    Represents a SQL data type, including optional length and scale.
    """

    sql_type: str
    length: int | None = None
    scale: int | None = None


class ColumnSettings(Settings, Noteable):
    """
    Settings for a column, including constraints, default value, and inline reference.
    """

    is_primary_key: bool = False
    is_null: bool | None = None
    is_unique: bool = False
    is_increment: bool = False
    default: Any | None = None
    ref: ReferenceInline | None = None
    checks: List[str] | None = None


class Column(Name):
    """
    Represents a table column, including its data type and settings.
    """

    data_type: DataType | Name
    settings: ColumnSettings | None = None


class IndexSettings(Settings, Noteable):
    """
    Settings for an index, including type, uniqueness, and primary key status.
    """

    idx_type: str | None = Field(default=None, alias="type")
    name: str | None = None
    is_unique: bool = False
    is_primary_key: bool = False


class Index(BaseModel):
    """
    Represents a table index, including columns and settings.
    """

    columns: Annotated[
        List[str], BeforeValidator(lambda v: v if not v or isinstance(v, List) else [v])
    ] = None
    settings: IndexSettings | None = None


class CheckSettings(Settings, Noteable):
    """
    Settings for a check, including name and expression.
    """

    name: str | None = None


class Check(BaseModel):
    """
    Represents a table check, including expression and settings.
    """

    expression: str
    settings: CheckSettings | None = None


class TableSettings(Settings, Noteable):
    """
    Settings for a table, including header color and notes.
    """

    header_color: str | None = Field(
        default=None, validation_alias=AliasChoices("headercolor", "headerColor")
    )


class TablePartial(Name):
    """
    Represents a partial table definition, including columns, indexes, and settings.
    """

    columns: List[Column]
    indexes: List[Index] | None = None
    checks: List[Check] | None = None
    settings: TableSettings | None = None


class Table(TablePartial, Noteable):
    """
    Represents a full table, including alias, partials, and ordering.
    """

    alias: str | None = None
    table_partials: List[str] | None = None
    table_partial_orders: Dict[str, int] | None = None


# Diagram
class Diagram(BaseModel):
    """
    Represents the entire DBML diagram, including project, enums, tables, references, and notes.
    """

    project: Project | None = None
    enums: List[Enum] | None = []
    table_groups: List[TableGroup] | None = []
    sticky_notes: List[Note] | None = []
    references: List[Reference] | None = []
    tables: List[Table] | None = []
    table_partials: List[TablePartial] | None = []
