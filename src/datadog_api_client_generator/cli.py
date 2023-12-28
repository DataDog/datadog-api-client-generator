import pathlib

import click
from datadog_api_client_generator.codegen.python.python_generator import PythonGenerator

from datadog_api_client_generator.openapi.utils import load_deref_yaml
from datadog_api_client_generator.openapi.openapi_model import OpenAPI


generators = {
    "python": PythonGenerator,
}


@click.command()
@click.argument(
    "specs",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=pathlib.Path),
    required=True,
)
@click.option("-g", "--generator", type=click.Choice(["python"]), required=True)
def cli(*args, **kwargs):
    specs = []
    for s in kwargs.get("specs"):
        spec = load_deref_yaml(s)
        spec = OpenAPI.model_validate(spec)
        specs.append(spec)

    output = kwargs.get("output")
    generator_cls = generators[kwargs.get("generator")]

    print("--------------------------------------------------------")

    generator = generator_cls(specs=specs, output=output)
    generator.generate()

    print("--------------------------------------------------------")
