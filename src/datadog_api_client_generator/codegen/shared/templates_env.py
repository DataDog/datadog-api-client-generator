import pathlib
import re
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from datadog_api_client_generator.codegen.shared.utils import camel_case, snake_case

from datadog_api_client_generator.openapi.openapi_model import OpenAPI


def default_filters() -> Dict[str, Any]:
    return {
        "camel_case": camel_case,
        "snake_case": snake_case,
    }


def default_globals(specs: Dict[str, OpenAPI]) -> Dict[str, Any]:
    return {"enumerate": enumerate, "openapi": specs}


def build_default_jinja2_env(specs: Dict[str, OpenAPI]) -> Environment:
    templates_dir = str(pathlib.Path(__file__).parent.parent / "python/templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    env.filters.update(default_filters())
    env.globals.update(default_globals(specs))

    return env
