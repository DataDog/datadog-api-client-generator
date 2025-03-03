# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
import re

PATTERN_WHITESPACE = re.compile(r"\W")
PATTERN_LEADING_ALPHA = re.compile(r"(.)([A-Z][a-z]+)")
PATTERN_FOLLOWING_ALPHA = re.compile(r"([a-z0-9])([A-Z])")
PATTERN_DOUBLE_UNDERSCORE = re.compile(r"__+")


def snake_case(value: str) -> str:
    value = PATTERN_LEADING_ALPHA.sub(r"\1_\2", value)
    value = PATTERN_FOLLOWING_ALPHA.sub(r"\1_\2", value).lower()
    value = PATTERN_WHITESPACE.sub("_", value)
    value = value.rstrip("_")
    return PATTERN_DOUBLE_UNDERSCORE.sub("_", value)


def camel_case(value):
    return "".join(x.title() for x in snake_case(value).split("_"))
