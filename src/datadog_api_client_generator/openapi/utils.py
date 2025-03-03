# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
from pathlib import PosixPath
from typing import Annotated, Any, Dict, Tuple, TypeVar, Union

import yaml
from jinja2 import Undefined
from pydantic import GetCoreSchemaHandler, PlainValidator
from pydantic_core import core_schema

HEADER_ANY_TYPE = "*/*"


# Annotated str class. Used to convert string to Bool values.
StrBool = Annotated[str, PlainValidator(lambda v: {"true": True, "false": False}[str(v).lower()])]


# Helper class that will always evaluate to falsey.
# We use this in schemas to help defferentiate between explicit null and omitted.
class Empty(Undefined):
    def __bool__(self) -> bool:
        return False

    def __copy__(self): ...

    def __deepcopy__(self, memo: Any): ...

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> any:
        return core_schema.any_schema()


T = TypeVar("T")
OptionalEmpty = Union[T, type(None), Empty]


def load_yaml(path: PosixPath) -> Dict:
    """Return openapi specification from yaml file."""
    with path.open() as fp:
        return yaml.load(fp, Loader=yaml.CSafeLoader)


def get_name_and_path_from_ref(ref: str) -> Tuple[str, str]:
    """Return name and path from $ref value."""
    return ref.split("/")[-2:]
