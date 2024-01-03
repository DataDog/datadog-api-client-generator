import pathlib

import click

from datadog_api_client_generator.codegen import GENERATORS
from datadog_api_client_generator.openapi.utils import load_yaml
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
    generator_cls = GENERATORS[kwargs.get("generator")]
    generator = generator_cls()

    output = kwargs.get("output")
    for s in kwargs.get("specs"):
        version = s.parent.name
        spec = load_yaml(s)
        spec = OpenAPI.model_validate(spec)

        print("--------------------------------------------------------")
        generator.generate(version=version, spec=spec, output=output)
        print("--------------------------------------------------------")
