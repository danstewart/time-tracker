# Need this file so pytest knows where the root is
# https://stackoverflow.com/questions/49028611/pytest-cannot-find-module

# Some fancy auto loading of fixtures from tests/fixtures
# https://gist.github.com/peterhurford/09f7dcda0ab04b95c026c60fa49c2a68

# If we just add a new fixture file in tests/fixtures it will be automatically in scope for each test

from glob import glob


def refactor(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = [
    refactor(fixture) for fixture in glob("tests/fixtures/*.py") if "__" not in fixture
]
