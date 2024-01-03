from jinja2 import Undefined
import yaml
from pathlib import PosixPath
from typing import Annotated, Any, Dict, Optional, Self, TypeVar, Union

from pydantic import GetCoreSchemaHandler, PlainValidator
from pydantic_core import core_schema
from jsonref import JsonRef


HEADER_ANY_TYPE = "*/*"


# Annotated str class. Used to convert string to Bool values.
StrBool = Annotated[str, PlainValidator(lambda v: {"true": True, "false": False}[str(v).lower()])]


# Helper class that will always evaluate to falsey.
# We use this in schemas to help defferentiate between explicit null and omitted.
class Empty(Undefined):
    def __bool__(self) -> bool:
        return False

    def __copy__(self):
        ...

    def __deepcopy__(self, memo: Any):
        ...

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> any:
        return core_schema.any_schema()


T = TypeVar("T")
OptionalEmpty = Union[T, type(None), Empty]


def load_yaml(path: PosixPath) -> Dict:
    """
    Return openapi specification from yaml file.
    """
    with path.open() as fp:
        return yaml.load(fp, Loader=yaml.CSafeLoader)


def get_name_from_json_ref(schema: Any) -> Optional[str]:
    """
    Return name if model is a ref.
    """
    if hasattr(schema, "__reference__"):
        return schema.__reference__["$ref"].split("/")[-1]
