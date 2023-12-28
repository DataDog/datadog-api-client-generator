from typing import Any, Dict

from datadog_api_client_generator.codegen.python import utils
from datadog_api_client_generator.codegen.shared.base_codegen import BaseCodegen, GeneratorConfig


class PythonGenerator(BaseCodegen):
    generator_config = GeneratorConfig()

    def generate(self):
        api_j2 = self.env.get_template("api.j2")
        # apis_j2 = self.env.get_template("apis.j2")
        # model_j2 = self.env.get_template("model.j2")
        # models_j2 = self.env.get_template("models.j2")
        # init_j2 = self.env.get_template("init.j2")
        # configuration_j2 = self.env.get_template("configuration.j2")

        # extra_files = {
        #     "api_client.py": self.env.get_template("api_client.j2"),
        #     "exceptions.py": self.env.get_template("exceptions.j2"),
        #     "model_utils.py": self.env.get_template("model_utils.j2"),
        #     "rest.py": self.env.get_template("rest.j2"),
        # }

    def additional_filters(self) -> Dict[str, Any]:
        return {
            "safe_snake_case": utils.safe_snake_case,
            "docstring": utils.docstring,
            "attribute_name": utils.attribute_name,
            "return_type": utils.return_type,
        }

    def additional_globals(self) -> Dict[str, Any]:
        return {}
