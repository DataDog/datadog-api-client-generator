from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import BaseModel


class ExternalDocs(BaseModel):
    url: str
    description: Optional[str] = None


class ServerVariable(BaseModel):
    default: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None


class Server(BaseModel):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = None
