from pathlib import Path

import pytest

from sqlfmt.cache import clear_cache, get_cache_file, write_cache
from sqlfmt.mode import Mode


@pytest.fixture
def cache_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    monkeypatch.setattr("sqlfmt.cache.user_cache_dir", lambda **kwargs: str(tmp_path))
    modes = [Mode(), Mode(line_length=40)]
    for mode in modes:
        write_cache({}, [], mode)
    return [get_cache_file(mode) for mode in modes]


def test_clear_all_configurations(cache_paths: list[Path]) -> None:
    clear_cache()
    assert not any(path.exists() for path in cache_paths)
