from lark_dbml import load, loads
from lark_dbml.converter import to_mermaid


def test_simple_table():
    dbml = """
    Table users {
      id int [pk]
      username varchar
    }
    """
    diagram = loads(dbml)
    mermaid = to_mermaid(diagram)

    expected = """erDiagram

users {
    int id PK
    varchar username
}
"""
    assert mermaid.strip() == expected.strip()


def test_relationships():
    dbml = """
    Table users {
      id int [pk]
    }
    Table posts {
      id int [pk]
      user_id int
    }
    Ref: posts.user_id > users.id
    """
    diagram = loads(dbml)
    mermaid = to_mermaid(diagram)

    # Check for correct relationship syntax
    # posts }o--|| users : "user_id - id"
    assert 'posts }o--|| users : "user_id - id"' in mermaid


def test_enums_and_notes():
    dbml = """
    Enum status {
      active
      inactive
    }
    Note "my_note" {
      "This is a note"
    }
    """
    diagram = loads(dbml)
    mermaid = to_mermaid(diagram)

    assert "%% Enum: status" in mermaid
    assert "%%   - active" in mermaid
    assert "%% Note: This is a note" in mermaid


def test_complex_dbml(example_path, expectation_path, standalone, parser):
    diagram = load(example_path / "complex.dbml", standalone, parser)

    mermaid = to_mermaid(diagram)

    with open(expectation_path / "complex_mermaid.md") as f:
        expectation = f.read()
    assert mermaid == expectation
