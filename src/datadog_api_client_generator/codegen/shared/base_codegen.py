from abc import ABC, abstractmethod
from typing import List

from datadog_api_client_generator.openapi.openapi_model import OpenAPI

class BaseCodegen(ABC):
    language: str

    def __init__(self, specs: List[OpenAPI]) -> None:
        self.specs = specs
    