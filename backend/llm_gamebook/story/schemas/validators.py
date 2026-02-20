from llm_gamebook.utils import normalized_kebab_case, normalized_pascal_case, normalized_snake_case


def is_normalized_kebab_case(v: str) -> str:
    if v != normalized_kebab_case(v):
        msg = "Invalid normalized kebab-case format"
        raise ValueError(msg)

    if not v:
        msg = "Invalid normalized kebab-case format"
        raise ValueError(msg)

    return v


def is_normalized_snake_case(v: str) -> str:
    if v != normalized_snake_case(v):
        msg = "Invalid normalized snake_case format"
        raise ValueError(msg)

    if not v:
        msg = "Invalid normalized snake_case format"
        raise ValueError(msg)

    return v


def is_normalized_pascal_case(v: str) -> str:
    if v != normalized_pascal_case(v):
        msg = "Invalid normalized PascalCase format"
        raise ValueError(msg)

    if not v:
        msg = "Invalid normalized PascalCase format"
        raise ValueError(msg)

    return v


def is_valid_project_id(value: str) -> str:
    namespace, name = value.split("/", 1)
    return f"{is_normalized_kebab_case(namespace)}/{is_normalized_kebab_case(name)}"
