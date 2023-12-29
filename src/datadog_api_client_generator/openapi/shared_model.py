from __future__ import annotations
from typing import Any, Dict, List, Optional

from jsonref import JsonRef
from pydantic import BaseModel, model_validator


class _Base(BaseModel):
    extensions: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    def _remap_extensions(cls, v: Any) -> Dict:
        if type(v) == JsonRef or type(v) == Dict:
            # Remap extensions
            extensions = {}
            for k in list(v.keys()):
                if k.startswith("x-"):
                    extensions[k] = v[k]
                    del v[k]
            if extensions:
                v["extensions"] = extensions

        return v


class ExternalDocs(_Base):
    url: str
    description: Optional[str] = None


class ServerVariable(_Base):
    default: str
    description: Optional[str] = None
    enum: Optional[List[str]] = list()


class Server(_Base):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = dict()
