from pathlib import Path

import pytest

from sqlfmt.mode import Mode


@pytest.mark.parametrize(
    "path,expected",
    [
        ("models/query_clickhouse.sql", "clickhouse"),
        ("models/query.sql", "polyglot"),
        ("query_clickhouse.sql/query.sql", "polyglot"),
        ("-", "polyglot"),
    ],
)
def test_filename_dialect(path: str, expected: str) -> None:
    mode = Mode(
        dialect_patterns={r"_clickhouse\.sql$": "clickhouse", "^-$": "clickhouse"}
    )
    assert mode.for_path(Path(path)).dialect_name == expected


def test_first_matching_pattern_wins() -> None:
    mode = Mode(dialect_patterns={r"\.sql$": "polyglot", "clickhouse": "clickhouse"})
    assert mode.for_path(Path("query_clickhouse.sql")).dialect_name == "polyglot"
