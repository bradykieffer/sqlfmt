import os
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional

from sqlfmt.dialect import ClickHouse, Polyglot
from sqlfmt.exception import SqlfmtConfigError


@dataclass
class Mode:
    """
    A Mode is a container for all sqlfmt config, including formatting config and
    report config. For more info on each option, see cli.py
    """

    SQL_EXTENSIONS: List[str] = field(default_factory=lambda: [".sql", ".sql.jinja"])
    dialect_name: str = "polyglot"
    dialect_patterns: Dict[str, str] = field(default_factory=dict)
    line_length: int = 88
    check: bool = False
    diff: bool = False
    exclude: List[str] = field(default_factory=list)
    exclude_root: Optional[Path] = None
    encoding: str = "utf-8"
    fast: bool = False
    single_process: bool = False
    no_jinjafmt: bool = False
    reset_cache: bool = False
    verbose: bool = False
    quiet: bool = False
    no_progressbar: bool = False
    no_color: bool = False
    force_color: bool = False

    def __post_init__(self) -> None:
        # get the dialect from its name.
        dialects = {
            "polyglot": Polyglot,
            "clickhouse": ClickHouse,
        }
        try:
            self.dialect = dialects[self.dialect_name.lower()]()
        except KeyError as e:
            raise SqlfmtConfigError(
                f"Mode was created with dialect_name={self.dialect_name}, "
                "which is not supported. Did you mean 'polyglot'?"
            ) from e

        if not isinstance(self.dialect_patterns, dict):
            raise SqlfmtConfigError("dialect_patterns must be a regex-to-dialect table")
        for pattern, dialect_name in self.dialect_patterns.items():
            if not isinstance(pattern, str) or not isinstance(dialect_name, str):
                raise SqlfmtConfigError(
                    "dialect_patterns keys and values must be strings"
                )
            if dialect_name.lower() not in dialects:
                raise SqlfmtConfigError(
                    f"Unsupported dialect {dialect_name!r} for pattern {pattern!r}"
                )
            try:
                re.compile(pattern)
            except re.error as e:
                raise SqlfmtConfigError(
                    f"Invalid dialect pattern {pattern!r}: {e}"
                ) from e

    def for_path(self, path: Path) -> "Mode":
        """Select the first dialect matching the filename; stdin uses the default."""
        if path != Path("-"):
            for pattern, dialect_name in self.dialect_patterns.items():
                if re.search(pattern, path.name):
                    return replace(self, dialect_name=dialect_name, dialect_patterns={})
        return self

    @property
    def color(self) -> bool:
        """
        There are 4 considerations for setting color:
        1. The --force-color option
        2. The --no-color option
        3. The NO_COLOR environment variable
        4. The default behavior, which is to colorize output

        This property checks these flags, in descending order of priority,
        and sets the authoritative flag accordingly

        See no-color.org for details.
        """
        if self.force_color:
            return True
        elif self.no_color:
            return False
        elif os.environ.get("NO_COLOR", False):
            return False
        else:
            return True
