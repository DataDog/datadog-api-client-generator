from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import PosixPath
from typing import List, Set

from jinja2 import Environment

from datadog_api_client_generator.codegen.shared.templates_env import build_default_jinja2_env
from datadog_api_client_generator.openapi.openapi_model import OpenAPI


@dataclass
class GeneratorConfig:
    keywords: Set[str] = field(default_factory=set)
    suffixes: Set[str] = field(default_factory=set)


class BaseCodegen(ABC):
    lanugage_config: GeneratorConfig

    def __init__(self, specs: List[OpenAPI], output: PosixPath) -> None:
        self.specs: List[OpenAPI] = specs
        self.env: Environment = build_default_jinja2_env()
        self.output: PosixPath = output

    @abstractmethod
    def generate(self):
        pass
