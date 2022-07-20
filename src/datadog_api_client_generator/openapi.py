import pathlib

from jsonref import JsonRef
from yaml import CSafeLoader
import yaml


def load(filename):
    path = pathlib.Path(filename)
    with path.open() as fp:
        return JsonRef.replace_refs(yaml.load(fp, Loader=CSafeLoader))


def apis(spec):
    operations = {}

    for path, endpoints in spec["paths"].items():
        for method, operation in endpoints.items():
            tag = operation["tags"][0]
            operations.setdefault(tag, []).append((path, method, operation))

    return operations
