"""Utility functions for tests."""


def normalize_newlines(s):
    """Normalize newlines to LF for cross-platform test comparison."""
    return s.replace("\r\n", "\n")


def compare_output(actual, expected):
    """Compare outputs ignoring extra blank lines."""
    actual_lines = [
        line for line in normalize_newlines(actual).split("\n") if line.strip()
    ]
    expected_lines = [
        line for line in normalize_newlines(expected).split("\n") if line.strip()
    ]
    return actual_lines == expected_lines
