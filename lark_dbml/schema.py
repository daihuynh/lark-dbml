from typing import Any, Annotated, Literal, List
from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from pydantic.aliases import AliasChoices


class Settings(BaseModel):
    model_config = ConfigDict(extra="allow")
    note: str | None = None


class Noteable(BaseModel):
    model_config = ConfigDict(extra="allow")
    note: str | None = Field(
        default=None, validation_alias=AliasChoices("note", "Note")
    )


class Name(BaseModel):
    db_schema: str | None = None
    name: str | None = None


# Project
class Project(Name, Noteable):
    database_type: str | None = None


# TableGroup
class TableGroup(Name, Noteable):
    tables: List[Name]
    settings: Settings | None = None


# Enum
class EnumValue(BaseModel):
    value: str
    settings: Settings | None = None


class Enum(Name):
    values: List[EnumValue]


# Sticky Note
class Note(Noteable):
    pass


# Relationship
class ReferenceInline(BaseModel):
    relationship: Literal["-", ">", "<", "<>"]
    to_table: Name
    to_columns: Annotated[
        List[str], BeforeValidator(lambda v: v if not v or isinstance(v, List) else [v])
    ] = None


class ReferenceSettings(Settings):
    delete: (
        Literal["cascade", "restrict", "set null", "set default", "no action"] | None
    ) = None
    update: (
        Literal["cascade", "restrict", "set null", "set default", "no action"] | None
    ) = None
    color: str | None = None  # For rendering


class Reference(Name, ReferenceInline):
    settings: ReferenceSettings | None = None
    from_table: Name | None = None
    from_columns: Annotated[
        List[str], BeforeValidator(lambda v: v if not v or isinstance(v, List) else [v])
    ] = None


# Table
class DataType(BaseModel):
    sql_type: str
    length: int | None = None
    scale: int | None = None


class ColumnSettings(Settings):
    is_primary_key: bool = False
    is_null: bool = True
    is_unique: bool = False
    is_increment: bool = False
    default: Any | None = None
    ref: ReferenceInline | None = None


class Column(Name):
    data_type: DataType | Name
    settings: ColumnSettings | None = None


class IndexSettings(Settings):
    idx_type: Literal["btree", "hash"] | None = Field(default=None, alias="type")
    name: str | None = None
    is_unique: bool = False
    is_primary_key: bool = False


class Index(BaseModel):
    columns: Annotated[
        List[str], BeforeValidator(lambda v: v if not v or isinstance(v, List) else [v])
    ] = None
    settings: IndexSettings | None = None


class TableSettings(Settings):
    header_color: str | None = Field(
        default=None, validation_alias=AliasChoices("headercolor", "headerColor")
    )


class TablePartial(Name):
    columns: List[Column]
    indexes: List[Index] | None = None
    settings: TableSettings | None = None


class Table(TablePartial, Noteable):
    alias: str | None = None
    table_partials: List[str] | None = None


# Diagram
class Diagram(BaseModel):
    project: Project | None = None
    enums: List[Enum] | None = []
    table_groups: List[TableGroup] | None = []
    sticky_notes: List[Note] | None = []
    references: List[Reference] | None = []
    tables: List[Table] | None = []
    table_partials: List[TablePartial] | None = []
