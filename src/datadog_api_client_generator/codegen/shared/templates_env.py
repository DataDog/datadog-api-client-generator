import re
import pathlib

from jinja2 import Environment, FileSystemLoader

from datadog_api_client_generator.codegen.shared.utils import camel_case, snake_case


def get_default_jinja2_env(templates_dir):
    env = Environment(loader=FileSystemLoader(str(pathlib.Path(__file__).parent / "templates")))
    
    # Filters
    env.filters["camel_case"] = camel_case
    env.filters["snake_case"] = snake_case
    
    # Globals
    env.globals["enumerate"] = enumerate