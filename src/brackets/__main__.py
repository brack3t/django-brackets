"""Commands for django-bracket developers."""
import contextlib
import sys
from typing import TYPE_CHECKING
from itertools import chain

import pytest

if TYPE_CHECKING:
    from os import PathLike
    from typing import List, Union
    SysResponse = Union[List[str], PathLike[str], None]

flag_groups = {
    "coverage": [
        "--cov",
        "--no-cov-on-fail",
        "--cov-report",
        "term-missing",
        "--cov-report",
        "xml",
    ],
    "standard": [
        "--nomigrations",
        "--random-order",
        "-c",
        "pyproject.toml",
    ],
}


def all_tests() -> SysResponse:
    """Run tests with official flags."""
    return [str(flag) for flag in chain(flag_groups.values())]


def no_coverage() -> SysResponse:
    """Run tests with official flags, sans coverage-related ones."""
    flags = flag_groups.copy()
    del flags["coverage"]
    return [str(flag) for flag in chain(flags.values())]


def standard() -> SysResponse:
    """Run with only the basic flags."""
    return [str(flag) for flag in flag_groups["standard"]]


if __name__ == "__main__":
    with contextlib.suppress(IndexError):
        arg: str = sys.argv[1] or ""

    match arg:
        case "all":
            test = all_tests
        case "no-cover":
            test = no_coverage
        case _:
            test = standard

    sys.exit(pytest.main(test()))
