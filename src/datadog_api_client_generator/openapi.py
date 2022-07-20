import pathlib

from jsonref import JsonRef
from yaml import CSafeLoader
import yaml


def load(filename):
    path = pathlib.Path(filename)
    with path.open() as fp:
        return JsonRef.replace_refs(yaml.load(fp, Loader=CSafeLoader))
