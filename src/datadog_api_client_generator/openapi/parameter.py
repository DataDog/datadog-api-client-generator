from __future__ import annotations
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field

from .schema import AllOfSchema, AnyOfSchema, BaseSchema, EnumSchema, ObjectSchema, OneOfSchema
from .utils import StrBool


class Parameter(BaseModel):
    in_: Literal["query", "header", "path", "cookie"] = Field(alias="in")
    name: str
    description: Optional[str] = None
    required: Optional[StrBool] = None
    deprecated: Optional[StrBool] = None
    schema: Optional[Union[AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, BaseSchema]] = None
    style: Optional[str] = None
    explode: Optional[StrBool] = None
    example: Optional[Any] = None