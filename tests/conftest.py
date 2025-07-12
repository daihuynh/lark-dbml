from pathlib import Path
from pytest import fixture


@fixture(scope="session")
def example_path() -> str:
    return Path(__file__).resolve().parent / ".." / "examples"


@fixture(scope="session")
def expectation_path() -> str:
    return Path(__file__).resolve().parent / "expectation"
