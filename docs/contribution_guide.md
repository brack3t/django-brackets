---
hide:
    - navigation
---
# Contributing

First of all, thank you for wanting to make `django-brackets` better! We love getting input and suggestions from the community. Secondly, we just want to put out a few ground rules for contributing so that we can get your pull requests in sooner and cause fewer headaches all around.

## Installation

When you want to install `django-brackets` for local development, first clone the project from GitHub. Secondly, install it as an editable package and install the testing and development dependencies: `pip install -e django-brackets[testing,development]`. You can test the project via `pytest` and check types with `mypy src`.

## Code of Conduct

Any communication around `django-brackets`, any contribution, any issue, is under the guidelines of the [Django code of conduct](https://www.djangoproject.com/conduct/). We don't allow any form of hate or discrimination in this project.

If you object to the code of conduct, you are not licensed to use this software.

## Code Style

All contributions require certain formatting and checks before they can be accepted. Your PR should:
- be formatted with `ruff` with an allowed line length of 88.
- have docstrings for all files, classes, and functions. Use `interrogate` to verify your work.
- be well-typed. We use `mypy` for static type checking. Run `mypy src` to check your types.
- maintain or increase code coverage.

## Tests

Your PR should also be well-tested. We use the `pytest` testing framework and make heavy use of fixtures over mocks. We aim for 100% test coverage but we also recognize that 100% is a magic number and won't prevent all bugs. Still, makes refactors easier!

We test `django-brackets` against the newest stable version of Python and the latest Long Term Support (LTS) release of Django. Other versions of Python and Django may work but are not tested against and, thus, unsupported.

## Documentation

Documentation is one of the most important parts of any project. If you don't know how to use it, you probably won't. All PRs should come with corresponding documentation updates. New mixins should come with a usage example and documentation explaining the concept. We use Mkdocs for our documentation needs.
