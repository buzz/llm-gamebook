from collections.abc import Callable

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


def id_from_name(data: object, generate_id: Callable[[str], str]) -> object:
    if isinstance(data, dict):
        try:
            name = data["name"]
        except KeyError:
            pass
        else:
            if isinstance(name, str) and "id" not in data:
                data["id"] = generate_id(name)
    return data
