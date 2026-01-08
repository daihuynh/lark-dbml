import os
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

def test_complex_dbml():
    """Test converting the complex.dbml example file."""
    # Construct path to examples/complex.dbml
    # Assuming tests run from repo root
    example_path = os.path.join("examples", "complex.dbml")

    diagram = load(example_path)
    mermaid = to_mermaid(diagram)

    # Assertions to ensure major components are present
    assert "erDiagram" in mermaid

    # Check for Tables
    assert '"another"."user" {' in mermaid
    assert '"example"."option" {' in mermaid
    assert '"example"."question" {' in mermaid
    assert '"example"."questionare" {' in mermaid

    # Check for Columns
    assert "varchar name" in mermaid
    assert "decimal value" in mermaid

    # Check for Enum (as comment)
    # The output seems to strip schema/quotes for enum name in convert
    assert '%% Enum: answer' in mermaid
    assert '%%   - n/a' in mermaid

    # Check for Project note (as comment)
    assert '%% Project: example' in mermaid

    # Check for Relationships
    # Ref fk_questionare_question: "example"."questionare".question_id > "example"."question".id
    # "example"."questionare" }o--|| "example"."question" : "question_id - id"
    assert '"example"."questionare" }o--|| "example"."question"' in mermaid
