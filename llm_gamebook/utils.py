import unicodedata

import casefy


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def normalized_snake_case(text: str) -> str:
    return casefy.snakecase(normalize(text))


def normalized_pascal_case(text: str) -> str:
    return casefy.pascalcase(normalize(text))
