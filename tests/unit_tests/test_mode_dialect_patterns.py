from typing import Any

import pytest

from sqlfmt.exception import SqlfmtConfigError
from sqlfmt.mode import Mode


@pytest.mark.parametrize(
    "patterns,message",
    [
        ({"[": "clickhouse"}, "Invalid dialect pattern"),
        ({".*": "unknown"}, "Unsupported dialect"),
        ({".*": 1}, "must be strings"),
        ([".*"], "must be a regex-to-dialect table"),
    ],
)
def test_invalid_dialect_patterns(patterns: Any, message: str) -> None:
    with pytest.raises(SqlfmtConfigError, match=message):
        Mode(dialect_patterns=patterns)
