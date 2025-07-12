from lark_dbml import load


def test_project(example_path):
    diagram = load(example_path / "project.dbml")

    # 'project literal included'
    assert diagram.project

    project = diagram.project
    assert project.name == "my_project"
    assert project.database_type == "Generic"
    assert project.note == ("Version: 1.0.0\n        Release: 01/01/2025")


def test_reference(example_path):
    diagram = load(example_path / "ref.dbml")

    # 'project literal included'
    assert len(diagram.references) == 2

    ref = diagram.references[0]
    assert ref.name == "name_optional"
    assert ref.from_table.db_schema == "schema1"
    assert ref.from_table.name == "table1"
    assert ref.from_columns == ["column1", "column2"]
    assert ref.relationship == "<"
    assert ref.to_table.db_schema == "schema2"
    assert ref.to_table.name == "table2"
    assert ref.to_columns == ["column1", "column2"]
    assert ref.settings.delete == "cascade"
    assert ref.settings.update == "no action"
    assert ref.settings.color == "#79AD51"

    ref = diagram.references[1]
    assert ref.name is None
    assert ref.from_table.db_schema == "schema1"
    assert ref.from_table.name == "table1"
    assert ref.from_columns == ["column1"]
    assert ref.relationship == "<"
    assert ref.to_table.db_schema == "schema2"
    assert ref.to_table.name == "table2"
    assert ref.to_columns == ["column2"]


def test_enum(example_path):
    diagram = load(example_path / "enum.dbml")

    assert len(diagram.enums) == 2

    enum = diagram.enums[0]
    assert enum.db_schema == "v2"
    assert enum.name == "job_status"
    assert len(enum.values) == 4
    assert enum.values[0].value == "created"
    assert enum.values[0].settings.note == "Waiting to be processed"
    assert enum.values[1].value == "running"
    assert enum.values[2].value == "done"
    assert enum.values[3].value == "failure"

    enum = diagram.enums[1]
    assert enum.db_schema is None
    assert enum.name == "grade"
    assert len(enum.values) == 4
    assert enum.values[0].value == "A+"
    assert enum.values[1].value == "A"
    assert enum.values[2].value == "A-"
    assert enum.values[3].value == "Not Yet Set"


def test_table_group(example_path):
    diagram = load(example_path / "table_group.dbml")

    assert len(diagram.table_groups) == 2

    group = diagram.table_groups[0]
    assert len(group.tables) == 2
    assert group.name == "e_commerce"
    assert group.tables[0].name == "merchants"
    assert group.tables[1].name == "countries"
    assert (
        group.settings.note == "Contains tables that are related to e-commerce system"
    )

    group = diagram.table_groups[1]
    assert len(group.tables) == 3
    assert group.name == "tablegroup_name"
    assert group.tables[0].name == "table1"
    assert group.tables[1].name == "table2"
    assert group.tables[2].name == "table3"
    assert group.note == "Contains tables that are related to e-commerce system"


def test_sticky_note(example_path):
    diagram = load(example_path / "sticky_note.dbml")

    assert len(diagram.sticky_notes) == 2
    assert diagram.sticky_notes[0].note == "This is a single line note"
    assert diagram.sticky_notes[1].note == (
        "This is a multiple lines note\n    This string can spans over multiple lines."
    )


def test_table_partial(example_path):
    diagram = load(example_path / "table_partial.dbml")

    assert len(diagram.table_partials) == 3
    table = diagram.table_partials[0]
    assert table.name == "base_template"
    assert table.settings.header_color == "#ff0000"
    assert len(table.columns) == 3
    assert table.columns[0].name == "id"
    assert table.columns[0].data_type.sql_type == "int"
    assert table.columns[0].settings.is_primary_key
    assert not table.columns[0].settings.is_null
    assert table.columns[1].name == "created_at"
    assert table.columns[1].data_type.sql_type == "timestamp"
    assert table.columns[1].settings.default == "`now()`"
    assert table.columns[2].name == "updated_at"
    assert table.columns[2].data_type.sql_type == "timestamp"
    assert table.columns[2].settings.default == "`now()`"

    table = diagram.table_partials[1]
    assert table.name == "soft_delete_template"
    assert len(table.columns) == 2
    assert table.columns[0].name == "delete_status"
    assert table.columns[0].data_type.sql_type == "boolean"
    assert not table.columns[0].settings.is_null
    assert table.columns[1].name == "deleted_at"
    assert table.columns[1].data_type.sql_type == "timestamp"
    assert table.columns[1].settings.default == "`now()`"

    table = diagram.table_partials[2]
    assert table.name == "email_index"
    assert len(table.columns) == 2
    assert table.columns[0].name == "email"
    assert table.columns[0].data_type.sql_type == "varchar"
    assert table.columns[0].data_type.length == 255
    assert table.columns[0].settings.is_unique
    assert table.columns[1].name == "value"
    assert table.columns[1].data_type.sql_type == "decimal"
    assert table.columns[1].data_type.length == 10
    assert table.columns[1].data_type.scale == 5
    assert len(table.indexes) == 2
    assert table.indexes[0].columns == ["email"]
    assert table.indexes[0].settings.name == "email_idx"
    assert table.indexes[0].settings.idx_type == "hash"
    assert table.indexes[0].settings.is_unique
    assert table.indexes[0].settings.is_primary_key
    assert table.indexes[1].columns == ["`sum(value)`", "email"]


def test_table(example_path):
    diagram = load(example_path / "table.dbml")

    # 'project literal included'
    assert len(diagram.tables) == 2
    assert len(diagram.table_partials) == 2

    # 1. TableA
    table = diagram.tables[0]
    assert table.name == "TableA"
    assert table.settings.note == "This is table A"
    assert len(table.columns) == 7
    # 1.1 Name check
    assert table.columns[0].name == "Id"
    assert table.columns[1].name == "BId"
    assert table.columns[2].name == "Name"
    assert table.columns[3].name == "IntValue"
    assert table.columns[4].name == "DecimalValue"
    assert table.columns[5].name == "DateValue"
    assert table.columns[6].name == "DateTimeValue"
    # 1.2 Type check
    assert table.columns[0].data_type.sql_type == "varchar"
    assert table.columns[0].data_type.length == 10
    assert table.columns[1].data_type.sql_type == "varchar"
    assert table.columns[1].data_type.length == 10
    assert table.columns[2].data_type.sql_type == "super string"
    assert table.columns[3].data_type.sql_type == "integer"
    assert table.columns[4].data_type.sql_type == "decimal"
    assert table.columns[4].data_type.length == 10
    assert table.columns[4].data_type.scale == 2
    assert table.columns[5].data_type.sql_type == "date"
    assert table.columns[6].data_type.sql_type == "datetime"
    # 1.3 Constraint
    assert table.columns[0].settings.is_primary_key
    assert not table.columns[0].settings.is_null
    assert table.columns[1].settings.ref.to_table.name == "TableB"
    assert table.columns[1].settings.ref.to_columns == ["Id"]
    assert table.columns[2].settings.is_unique
    assert table.columns[3].settings.is_null
    assert table.columns[4].settings.default == 10.24
    # 1.4 Comments
    assert table.columns[2].settings.note == "Name"
    assert table.columns[3].settings.note == "Integer Value"

    # 2. TablePartial B
    table = diagram.table_partials[0]
    assert table.name == "TableB"
    assert table.columns[0].name == "Id"
    assert table.columns[0].data_type.sql_type == "varchar"
    assert table.columns[0].data_type.length == 10
    assert table.columns[0].settings.is_primary_key
    assert not table.columns[0].settings.is_null

    # 2. TableParital C
    table = diagram.table_partials[1]
    assert table.name == "TableC"
    assert table.columns[0].name == "IntValue"
    assert table.columns[0].data_type.sql_type == "integer"
    assert table.columns[0].settings.ref.to_table.name == "TableA"
    assert table.columns[0].settings.ref.to_columns == ["IntValue"]

    # 4. TableC
    table = diagram.tables[1]
    assert table.db_schema == "schema1"
    assert table.name == "Table D"
    assert table.alias == "D"
    assert table.columns[0].name == "Name"
    assert table.columns[0].data_type.sql_type == "super string"
    assert len(table.table_partials) == 2
    assert table.table_partials == ["TableB", "TableC"]
    assert table.note == "Includes TableB & TableC"
