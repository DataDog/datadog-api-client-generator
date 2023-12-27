import yaml
import pathlib
from typing import Annotated, Dict, Optional

from pydantic import PlainValidator
from jsonref import JsonRef


HEADER_ANY_TYPE = "*/*"


StrBool = Annotated[str, PlainValidator(lambda v: {"true": True, "false": False}[str(v).lower()])]


def load_deref_yaml(path: pathlib.PosixPath) -> Dict:
    with path.open() as fp:
        return JsonRef.replace_refs(yaml.load(fp, Loader=yaml.CSafeLoader))


def get_name_from_json_ref(schema) -> Optional[str]:
    if hasattr(schema, "__reference__"):
        return schema.__reference__["$ref"].split("/")[-1]
