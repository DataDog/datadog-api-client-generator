from typing import Annotated
from pydantic import PlainValidator
import yaml
import pathlib

from jsonref import JsonRef


NONE_TYPE = ""

StrBool = Annotated[str, PlainValidator(lambda v: {"true": True, "false": False}[str(v).lower()])]


def load(filename):
    path = pathlib.Path(filename)
    with path.open() as fp:
        return JsonRef.replace_refs(yaml.load(fp, Loader=yaml.CSafeLoader))


def get_name(schema):
    if hasattr(schema, "__reference__"):
        return schema.__reference__["$ref"].split("/")[-1]
