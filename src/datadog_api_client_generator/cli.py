import pprint
import pathlib

import click

from .openapi.utils import load_deref_yaml
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
@click.option("-l", "--language", type=click.Choice(["python"]), required=True)
def cli(*args, **kwargs):
    for p in kwargs.get("specs"):
        spec = load_deref_yaml(p)
        spec = OpenAPI.model_validate(spec)
        print("--------------------------------------------------------")

        # path = spec.paths.get("/api/v1/dashboard/lists/manual")
        # pp.pprint(path.post.accept_headers())

        # for k, v in spec.components.schemas.items():
        #     print(f"{k} -- type ::: ", type(v))

        print("--------------------------------------------------------")
