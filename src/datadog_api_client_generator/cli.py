import pprint
import pathlib

import click

from .openapi.utils import load
from .openapi.openapi import OpenAPI


pp = pprint.PrettyPrinter()


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
def cli(specs, output):
    for p in specs:
        spec = load(p)
        spec = OpenAPI.model_validate(spec)
        print("--------------------------------------------------------")
        pp.pprint(spec.model_dump())

        for k, v in spec.components.schemas.items():
            print(f"{k} -- type ::: ", type(v))
        print("--------------------------------------------------------")
