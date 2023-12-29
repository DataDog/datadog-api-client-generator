import pathlib

import click

from datadog_api_client_generator.codegen import GENERATORS
from datadog_api_client_generator.openapi.utils import load_deref_yaml
from datadog_api_client_generator.openapi.openapi_model import OpenAPI


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
@click.option("-g", "--generator", type=click.Choice(list(GENERATORS.keys())), required=True)
def cli(*args, **kwargs):
    specs = {}
    for s in kwargs.get("specs"):
        version = s.parent.name
        spec = load_deref_yaml(s)
        spec = OpenAPI.model_validate(spec)

        specs[s] = spec

    output = kwargs.get("output")
    generator_cls = GENERATORS[kwargs.get("generator")]

    print("--------------------------------------------------------")

    generator = generator_cls(specs=specs, output=output)
    generator.generate()

    print("--------------------------------------------------------")
