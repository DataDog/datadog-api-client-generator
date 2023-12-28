import pathlib
import re
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader


PATTERN_WHITESPACE = re.compile(r"\W")
PATTERN_LEADING_ALPHA = re.compile(r"(.)([A-Z][a-z]+)")
PATTERN_FOLLOWING_ALPHA = re.compile(r"([a-z0-9])([A-Z])")
PATTERN_DOUBLE_UNDERSCORE = re.compile(r"__+")


def snake_case(value: str) -> str:
    value = PATTERN_LEADING_ALPHA.sub(r"\1_\2", value)
    value = PATTERN_FOLLOWING_ALPHA.sub(r"\1_\2", value).lower()
    value = PATTERN_WHITESPACE.sub("_", value)
    value = value.rstrip("_")
    return PATTERN_DOUBLE_UNDERSCORE.sub("_", value)


def camel_case(value: str) -> str:
    return "".join(x.title() for x in snake_case(value).split("_"))


def default_filters() -> Dict[str, Any]:
    return {
        "camel_case": camel_case,
        "snake_case": snake_case,
    }


def default_globals() -> Dict[str, Any]:
    return {
        "enumerate": enumerate,
    }


def build_default_jinja2_env() -> Environment:
    templates_dir = str(pathlib.Path(__file__).parent.parent / "python/templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    env.filters.update(default_filters())
    env.globals.update(default_globals())
