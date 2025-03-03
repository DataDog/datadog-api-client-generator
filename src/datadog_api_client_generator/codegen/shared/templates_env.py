# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
import pathlib
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from datadog_api_client_generator.codegen.shared.utils import camel_case, snake_case


def default_filters() -> Dict[str, Any]:
    return {
        "camel_case": camel_case,
        "snake_case": snake_case,
    }


def default_globals() -> Dict[str, Any]:
    return {"enumerate": enumerate}


def build_default_jinja2_env() -> Environment:
    templates_dir = str(pathlib.Path(__file__).parent.parent / "python/templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    env.filters.update(default_filters())
    env.globals.update(default_globals())

    return env
