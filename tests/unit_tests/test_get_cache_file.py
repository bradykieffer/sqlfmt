from dataclasses import replace

import pytest

from sqlfmt.cache import get_cache_file
from sqlfmt.mode import Mode


@pytest.mark.parametrize(
    "changes",
    [
        {"dialect_name": "clickhouse"},
        {"line_length": 40},
        {"no_jinjafmt": True},
        {"encoding": "utf-16"},
        {"fast": True},
        {"dialect_patterns": {"clickhouse": "clickhouse"}},
    ],
)
def test_formatting_config_changes_cache(changes: dict) -> None:
    assert get_cache_file(Mode(**changes)) != get_cache_file(Mode())


def test_pattern_order_changes_cache() -> None:
    patterns = {".*": "polyglot", "clickhouse": "clickhouse"}
    assert get_cache_file(Mode(dialect_patterns=patterns)) != get_cache_file(
        Mode(dialect_patterns=dict(reversed(list(patterns.items()))))
    )


def test_reporting_config_preserves_cache() -> None:
    mode = Mode()
    assert get_cache_file(mode) == get_cache_file(
        replace(mode, check=True, verbose=True, single_process=True)
    )
