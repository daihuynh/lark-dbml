from lark_dbml import load
from lark_dbml.converter import to_sql


def test_sql(example_path, expectation_path):
    diagram = load(example_path / "complex.dbml")

    sql = to_sql(diagram)

    with open(expectation_path / "complex_postgres.sql") as f:
        expectation = f.read()
    assert sql == expectation
