from lark_dbml import load
from lark_dbml.converter import to_sql, from_sql
from pathlib import Path

import pytest
import difflib
from sqlglot import parse, Dialects


def test_sql(example_path, expectation_path, standalone, parser):
    diagram = load(example_path / "complex.dbml", standalone, parser)

    sql = to_sql(diagram)

    with open(expectation_path / "complex_postgres.sql") as f:
        expectation = f.read()
    assert sql == expectation


@pytest.mark.parametrize(
    "sql_file",
    [f.name for f in Path(__file__).parents[1].joinpath("expectation").glob("*.sql")],
)
def test_load_sql(example_path, expectation_path, standalone, parser, sql_file):
    with open(expectation_path / sql_file) as f:
        ddl = f.read()

    diagram = from_sql(ddl=ddl)

    generated_sql = to_sql(diagram)

    # Normalize both SQLs to ensure comparison ignores formatting/whitespace differences
    # We use sqlglot to parse and regenerate the SQL for both
    original_exprs = [
        e.sql(dialect=Dialects.POSTGRES)
        for e in parse(ddl, dialect=Dialects.POSTGRES)
        if e
    ]
    generated_exprs = [
        e.sql(dialect=Dialects.POSTGRES)
        for e in parse(generated_sql, dialect=Dialects.POSTGRES)
        if e
    ]

    # Verify they have the same number of statements
    assert len(original_exprs) == len(generated_exprs)

    # Compare each statement
    diffs = []
    for i, (orig, gen) in enumerate(zip(original_exprs, generated_exprs)):
        if orig != gen:
            diffs.append(f"Statement {i} mismatch:")
            diffs.extend(
                difflib.unified_diff(
                    [orig + "\n"], [gen + "\n"], fromfile="Original", tofile="Generated"
                )
            )

    if diffs:
        assert False, "\n".join(diffs)
