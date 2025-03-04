# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
import logging
import pathlib

import click

from datadog_api_client_generator.codegen import GENERATORS
from datadog_api_client_generator.openapi.openapi_model import OpenAPI
from datadog_api_client_generator.openapi.utils import load_yaml

logger = logging.getLogger(__name__)

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
def cli(*_args, **kwargs):
    generator_cls = GENERATORS[kwargs.get("generator")]
    generator = generator_cls()

    output = kwargs.get("output")
    specs = {}
    for s in kwargs.get("specs"):
        version = s.parent.name
        spec = load_yaml(s)
        spec = OpenAPI.model_validate(spec, context={})
        specs[version] = spec

    logging.info("--------------------------------------------------------")
    generator.generate(specs=specs, output=output)
    logging.info("--------------------------------------------------------")
