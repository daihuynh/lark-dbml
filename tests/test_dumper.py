import tempfile
from io import StringIO
from lark_dbml import load, dump, dumps


def test_dump(example_path, standalone, parser):
    diagram = load(example_path / "project.dbml", standalone, parser)
    dbml = dumps(diagram)

    assert (
        dbml
        == """Project my_project {
    database_type: 'Generic'
    note: '''Version: 1.0.0
        Release: 01/01/2025'''
    version: '1.0.0'
}

"""
    )


def test_dumps(example_path, standalone, parser):
    diagram = load(example_path / "project.dbml", standalone, parser)
    with StringIO() as f:
        dump(diagram, file=f)
        dbml = f.getvalue()

    assert (
        dbml
        == """Project my_project {
    database_type: 'Generic'
    note: '''Version: 1.0.0
        Release: 01/01/2025'''
    version: '1.0.0'
}

"""
    )

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".dbml", delete=True) as f:
        dump(diagram, file=f.name)

        dbml = f.read()
        assert (
            dbml
            == """Project my_project {
    database_type: 'Generic'
    note: '''Version: 1.0.0
        Release: 01/01/2025'''
    version: '1.0.0'
}

"""
        )
