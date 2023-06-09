"""Commands for django-bracket developers."""
import contextlib
from itertools import chain
import sys

import pytest

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


def all_tests() -> int:
    """Run tests with official flags."""
    return [str(flag) for flag in chain(flag_groups.values())]


def no_coverage() -> int:
    """Run tests with official flags, sans coverage-related ones."""
    flags = flag_groups.copy()
    del flags["coverage"]
    return [str(flag) for flag in chain(flags.values())]


if __name__ == "__main__":
    arg: str = ""
    with contextlib.suppress(IndexError):
        arg: str = sys.argv[1]

    match arg:
        case "no-cover":
            test = no_coverage
        case _:
            test = all_tests

    sys.exit(pytest.main(test()))
