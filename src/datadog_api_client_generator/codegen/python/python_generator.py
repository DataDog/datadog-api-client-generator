import keyword

from datadog_api_client_generator.codegen.shared.base_codegen import BaseCodegen, GeneratorConfig


KEYWORDS = set(keyword.kwlist)
KEYWORDS.add("property")
KEYWORDS.add("cls")


class PythonGenerator(BaseCodegen):
    generator_config = GeneratorConfig(
        keywords=KEYWORDS,
    )

    def generate(self):
        print("we are running generator")
        pass
