from textwrap import dedent
from lark_dbml import Diagram
from lark_dbml.converter.dbml.base import DBMLConverterSettings
from lark_dbml.schema import (
    Column,
    ColumnSettings,
    DataType,
    Enum,
    EnumValue,
    EnumValueSettings,
    Index,
    IndexSettings,
    Name,
    Note,
    Project,
    Reference,
    ReferenceInline,
    ReferenceSettings,
    Table,
    TableGroup,
    TablePartial,
    TableSettings,
)

from lark_dbml.converter import to_dbml


def test_project():
    diagram = Diagram(
        project=Project(
            name="Example", note="It's a note", database_type="Generic", Version="1.0.0"
        )
    )

    dbml = to_dbml(diagram)

    assert (
        dbml
        == r"""Project Example {
    Version: '1.0.0'
    database_type: 'Generic'
    note: 'It\'s a note'
}

"""
    )


def test_enum():
    diagram = Diagram(
        enums=[
            Enum(
                db_schema="my schema",
                name="status",
                values=[
                    EnumValue(value="n/a"),
                    EnumValue(value="yes", settings=EnumValueSettings(note="or True")),
                    EnumValue(value="no", settings=EnumValueSettings(note="or False")),
                    EnumValue(
                        value="other",
                        settings=EnumValueSettings(
                            note=dedent("""
                                    Either
                                    or
                                    True
                                    or
                                    False
                                    """),
                            server_note="Do not implement",
                        ),
                    ),
                ],
            )
        ]
    )
    dbml = to_dbml(diagram, settings=DBMLConverterSettings(allow_extra=True))
    assert (
        dbml
        == """Enum "my schema"."status" {
    "n/a"
    yes [note: 'or True']
    no [note: 'or False']
    other [note: '''
Either
or
True
or
False
''', server_note: 'Do not implement']
}

"""
    )


def test_reference():
    diagram = Diagram(
        references=[
            Reference(
                relationship="-",
                from_table=Name(name="TableA"),
                from_columns=["Id"],
                to_table=Name(db_schema="schemaB", name="TableB"),
                to_columns=["TableAId"],
                settings=ReferenceSettings(note="This is not valid in DBML yet!"),
            )
        ]
    )

    dbml = to_dbml(diagram, settings=DBMLConverterSettings(allow_extra=True))
    assert (
        dbml
        == "Ref: TableA.Id - schemaB.TableB.TableAId [note: 'This is not valid in DBML yet!']\n\n"
    )

    diagram = Diagram(
        references=[
            Reference(
                relationship="-",
                from_table=Name(db_schema="my schema", name="TableC"),
                from_columns=["Id", "Value"],
                to_table=Name(db_schema="your schema", name="TableD"),
                to_columns=["CId", "CValue"],
                name="fk_TableC_TablD_Id_Value",
                settings=ReferenceSettings(delete="cascade", color="#F00"),
            )
        ]
    )

    dbml = to_dbml(diagram)
    assert (
        dbml
        == 'Ref fk_TableC_TablD_Id_Value: "my schema"."TableC".(Id,Value) - "your schema"."TableD".(CId,CValue) [color: #F00, delete: cascade]\n\n'
    )


def test_sticky_note():
    diagram = Diagram(
        sticky_notes=[
            Note(name="single_line_note", note="This ' should be quoted"),
            Note(
                name="multiple_lines_note",
                note="""
This is a multiple lines note
This string can spans over multiple lines.
""",
            ),
        ]
    )

    dbml = to_dbml(diagram)
    assert (
        dbml
        == r"""Note single_line_note {
'This \' should be quoted'
}

Note multiple_lines_note {
'''
This is a multiple lines note
This string can spans over multiple lines.
'''
}

"""
    )


def test_table_group():
    diagram = Diagram(
        table_groups=[
            TableGroup(
                name="group A",
                tables=[
                    Name(db_schema="my schema", name="TableC"),
                    Name(name="TableA"),
                ],
            )
        ]
    )

    dbml = to_dbml(diagram)
    assert (
        dbml
        == """TableGroup "group A" {
    "my schema"."TableC"
    TableA
}

"""
    )


def test_table_partial():
    diagram = Diagram(
        table_partials=[
            TablePartial(
                name="my table",
                columns=[
                    Column(
                        name="id",
                        data_type=DataType(sql_type="int"),
                        settings=ColumnSettings(is_primary_key=True, is_increment=True),
                    ),
                    Column(
                        name="some_status",
                        data_type=Name(db_schema="public", name="status"),
                        settings=ColumnSettings(default="yes"),
                    ),
                    Column(
                        name="fkey",
                        data_type=DataType(sql_type="super string"),
                        settings=ColumnSettings(
                            ref=ReferenceInline(
                                relationship="-",
                                to_table=Name(
                                    db_schema="your schema", name="your table"
                                ),
                                to_columns=["superid"],
                            ),
                            is_null=False,
                            is_unique=True,
                        ),
                    ),
                    Column(
                        name="name", data_type=DataType(sql_type="varchar", length=50)
                    ),
                    Column(
                        name="value",
                        data_type=DataType(sql_type="decimal", length=10, scale=2),
                    ),
                    Column(
                        name="to_date",
                        data_type=DataType(sql_type="datetime"),
                        settings=ColumnSettings(
                            default="`getdate()`", comment="column metadata"
                        ),
                    ),
                ],
            )
        ]
    )

    dbml = to_dbml(diagram, DBMLConverterSettings(allow_extra=True))
    assert (
        dbml
        == """TablePartial "my table" {
    id int [pk, increment]
    some_status public.status [null, default: "yes"]
    fkey "super string" [ref: - "your schema"."your table".superid, not null, unique]
    name varchar(50)
    value decimal(10,2)
    to_date datetime [null, comment: 'column metadata', default: `getdate()`]
}

"""
    )


def test_table():
    diagram = Diagram(
        table_partials=[
            TablePartial(
                name="header",
                columns=[
                    Column(
                        name="name", data_type=DataType(sql_type="varchar", length=50)
                    )
                ],
            ),
            TablePartial(
                name="footer",
                columns=[
                    Column(
                        name="to_date",
                        data_type=DataType(sql_type="timestamp"),
                        settings=ColumnSettings(default="`now()`"),
                    )
                ],
            ),
        ],
        tables=[
            Table(
                name="body",
                alias="full_table",
                note="Incorporated with header and footer",
                settings=TableSettings(
                    headercolor="#3498DB", note="header note", partitioned_by="id"
                ),
                columns=[
                    Column(
                        name="id",
                        data_type=DataType(sql_type="int"),
                        settings=ColumnSettings(
                            is_primary_key=True, note="why is id behind name?"
                        ),
                    ),
                    Column(
                        name="audit_date",
                        data_type=DataType(sql_type="timestamp"),
                        settings=ColumnSettings(default="`getdate()`"),
                    ),
                ],
                table_partials=["header", "footer"],
                table_partial_orders={"header": 1, "footer": 3},
                indexes=[
                    Index(
                        columns=["id", "name"],
                        settings=IndexSettings(
                            is_primary_key=True, note="This is not valid in DBML yet!"
                        ),
                    ),
                    Index(
                        columns=["`value*3`, `now()`"],
                        settings=IndexSettings(
                            name="triple_value_now", type="hash", is_unique=True
                        ),
                    ),
                ],
            )
        ],
    )

    dbml = to_dbml(diagram, settings=DBMLConverterSettings(allow_extra=True))
    assert (
        dbml
        == """TablePartial header {
    name varchar(50)
}

TablePartial footer {
    to_date timestamp [null, default: `now()`]
}

Table body as full_table [note: 'header note', headercolor: #3498DB, partitioned_by: 'id'] {
    ~header
    id int [pk, note: 'why is id behind name?']
    ~footer
    audit_date timestamp [null, default: `getdate()`]
    indexes {
        (id,name) [pk, note: 'This is not valid in DBML yet!']
        (`value*3`, `now()`) [unique, name: 'triple_value_now', type: hash]
    }

    Note: 'Incorporated with header and footer'
}

"""
    )
