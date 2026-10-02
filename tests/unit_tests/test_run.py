from pathlib import Path

from sqlfmt.api import run
from sqlfmt.mode import Mode


def test_dialect_change_reformats_unchanged_file(tmp_path: Path) -> None:
    # agent-check: multiple-asserts -- verify cache hits and config invalidation
    path = tmp_path / "query.sql"
    path.write_text("select MyFunction(MyField) as MyAlias\n")
    mode = Mode(dialect_name="clickhouse", single_process=True)
    run([path], mode)
    assert run([path], mode).results[0].from_cache
    result = run([path], Mode(single_process=True)).results[0]
    assert not result.from_cache
    assert result.formatted_string == "select myfunction(myfield) as myalias\n"


def test_multiprocessing_only_formats_cache_misses(tmp_path: Path) -> None:
    # agent-check: multiple-asserts -- each input must produce exactly one result
    cached = tmp_path / "cached.sql"
    cached.write_text("select 1\n")
    mode = Mode()
    run([cached], mode)
    paths = [cached, tmp_path / "one.sql", tmp_path / "two.sql"]
    for path in paths[1:]:
        path.write_text("select 1\n")
    results = run(paths, mode).results
    assert len(results) == len(paths)
    assert sum(result.from_cache for result in results) == 1
