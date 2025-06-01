from typing import Any

from llm_gamebook.utils import normalized_pascal_case, normalized_snake_case


def is_normalized_snake_case(v: str) -> str:
    if v != normalized_snake_case(v):
        msg = "Invalid normalized snake_case format"
        raise ValueError(msg)
    return v


def is_normalized_pascal_case(v: str) -> str:
    if v != normalized_pascal_case(v):
        msg = "Invalid normalized PascalCase format"
        raise ValueError(msg)
    return v


def pascal_case_from_name(v: Any) -> Any:
    if isinstance(v, dict):
        try:
            name = v["name"]
        except KeyError:
            pass
        else:
            if "id" not in v:
                v["id"] = normalized_pascal_case(name)
    return v


def snake_case_from_name(v: Any) -> Any:
    if isinstance(v, dict):
        try:
            name = v["name"]
        except KeyError:
            pass
        else:
            if "id" not in v:
                v["id"] = normalized_snake_case(name)
    return v
