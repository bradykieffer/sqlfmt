from pathlib import Path

import pytest
from click.testing import CliRunner

from sqlfmt.cli import sqlfmt


@pytest.mark.parametrize(
    "args,expected",
    [
        ([], "select MyFunction(MyField) as MyAlias\n"),
        (["--dialect", "polyglot"], "select myfunction(myfield) as myalias\n"),
    ],
)
def test_filename_dialect_config(
    tmp_path: Path, args: list[str], expected: str
) -> None:
    # agent-check: multiple-asserts -- validate CLI success and output from TOML rules
    config = tmp_path / "pyproject.toml"
    config.write_text(
        "[tool.sqlfmt]\ndialect = 'polyglot'\n"
        "[tool.sqlfmt.dialect_patterns]\n"
        "'_clickhouse\\.sql$' = 'clickhouse'\n"
    )
    path = tmp_path / "query_clickhouse.sql"
    path.write_text("select MyFunction(MyField) as MyAlias\n")
    result = CliRunner().invoke(sqlfmt, [str(path), "--config", str(config), *args])
    assert result.exit_code == 0, result.exception
    assert path.read_text() == expected


def test_environment_dialect_overrides_patterns(tmp_path: Path) -> None:
    # agent-check: multiple-asserts -- validate environment precedence and output
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool.sqlfmt.dialect_patterns]\n'.*' = 'clickhouse'\n")
    path = tmp_path / "query.sql"
    path.write_text("select MyField\n")
    result = CliRunner().invoke(
        sqlfmt,
        [str(path), "--config", str(config)],
        env={"SQLFMT_DIALECT": "polyglot"},
    )
    assert result.exit_code == 0, result.exception
    assert path.read_text() == "select myfield\n"
