import os
import tempfile
from io import StringIO

from lark_dbml import dump, dumps, load

from .utils import compare_output


def test_dump(example_path, standalone, parser):
    diagram = load(example_path / "project.dbml", standalone, parser)
    dbml = dumps(diagram)

    assert compare_output(
        dbml,
        """Project my_project {
    database_type: 'Generic'
    note: '''Version: 1.0.0
        Release: 01/01/2025'''
    version: '1.0.0'
}

""",
    )


def test_dumps(example_path, standalone, parser):
    diagram = load(example_path / "project.dbml", standalone, parser)
    with StringIO() as f:
        dump(diagram, file=f)
        dbml = f.getvalue()

    assert compare_output(
        dbml,
        """Project my_project {
    database_type: 'Generic'
    note: '''Version: 1.0.0
        Release: 01/01/2025'''
    version: '1.0.0'
}

""",
    )

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".dbml", delete=False) as f:
        temp_path = f.name
    try:
        dump(diagram, file=temp_path)
        with open(temp_path, mode="r", encoding="utf-8") as f:
            dbml = f.read()
        assert compare_output(
            dbml,
            """Project my_project {
    database_type: 'Generic'
    note: '''Version: 1.0.0
        Release: 01/01/2025'''
    version: '1.0.0'
}

""",
        )
    finally:
        os.unlink(temp_path)
