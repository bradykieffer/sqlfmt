import hashlib
import json
import pickle
from importlib import metadata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from platformdirs import user_cache_dir

from sqlfmt.mode import Mode
from sqlfmt.report import STDIN_PATH, SqlFormatResult

Cache = Dict[Path, Tuple[float, int]]


def get_cache_file(mode: Optional[Mode] = None) -> Path:
    """
    Returns the path to the cache file on disk
    """
    sqlfmt_version = metadata.version("shandy-sqlfmt")
    cache_dir = Path(user_cache_dir(appname="sqlfmt"))
    mode = mode or Mode()
    formatting_config = (
        mode.dialect_name.lower(),
        mode.line_length,
        mode.no_jinjafmt,
        mode.encoding,
        mode.fast,
    )
    digest = hashlib.sha256(json.dumps(formatting_config).encode()).hexdigest()
    cache_file = cache_dir / f"cache-{sqlfmt_version}-{digest}.pickle"
    return cache_file


def load_cache(mode: Optional[Mode] = None) -> Cache:
    """
    Returns a Cache (a dictionary keyed by file path) by loading
    from a pickle saved to disk
    """
    cache_file = get_cache_file(mode)
    try:
        with cache_file.open("rb") as f:
            cache: Cache = pickle.load(f)
            return cache
    except (
        pickle.UnpicklingError,
        ValueError,
        IndexError,
        FileNotFoundError,
        ModuleNotFoundError,
    ):
        return {}


def check_cache(cache: Cache, p: Path) -> bool:
    """
    Returns True if the path is in the cache and the cached stats match the
    file on disk
    """
    if p == STDIN_PATH or not cache:
        return False
    else:
        path = p.resolve()
        if path in cache:
            return _get_cache_info(path) == cache[path]
        else:
            return False


def write_cache(cache: Cache, results: List[SqlFormatResult], mode: Mode) -> None:
    """
    Updates cache with results, then dumps cache to disk
    """
    cache_file = get_cache_file(mode)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    new_cache = cache.copy()
    for path in _gen_cache_keys_for_updates(results, mode):
        updated_info = _get_cache_info(path)
        new_cache[path] = updated_info
    with open(cache_file, "wb") as f:
        pickle.dump(new_cache, f)


def clear_cache() -> None:
    """
    Deletes all sqlfmt cache files on disk, if they exist.
    """
    for p in get_cache_file().parent.glob("cache-*.pickle"):
        try:
            p.unlink()
        except FileNotFoundError:
            pass


def _get_cache_info(path: Path) -> Tuple[float, int]:
    """
    Returns a tuple of (modified_time, file_size) for the path; this tuple is
    persisted to the cache, and we check the files on disk against this cached
    value to determine if we need to format the file again
    """
    stat = path.resolve().stat()
    file_info = (stat.st_mtime, stat.st_size)
    return file_info


def _gen_cache_keys_for_updates(
    results: Iterable[SqlFormatResult], mode: Mode
) -> Iterable[Path]:
    """
    Takes an interable of SqlfmtResults and yields paths to files that should
    be updated in the cache, based on the result of the sqlfmt run
    """
    gen = (
        res.source_path.resolve()
        for res in results
        if res.source_path
        and res.source_path != STDIN_PATH
        and _should_update_cache(res, mode)
    )
    yield from gen


def _should_update_cache(result: SqlFormatResult, mode: Mode) -> bool:
    """
    Takes a single SqlfmtResult and returns True if that result indicates that
    the associated file should be updated in the cache
    """
    if result.has_error or result.from_cache:
        return False
    elif not result.has_changed:
        return True
    elif mode.check or mode.diff:
        return False
    else:
        return True
