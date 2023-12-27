import pprint
import pathlib

import click

from .openapi.utils import load_deref_yaml
from .openapi.openapi import OpenAPI


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
@click.option("-l", "--language", type=click.Choice(["python"]), required=True)
def cli(*args, **kwargs):
    for p in kwargs.get("specs"):
        spec = load_deref_yaml(p)
        print("type ", type(spec))
        spec = OpenAPI.model_validate(spec)
        print("--------------------------------------------------------")

        print("--------------------------------------------------------")
