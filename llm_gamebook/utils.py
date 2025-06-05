import re
import unicodedata

import casefy

think_block_re = re.compile(r"<think>\s*(.*?)\s*</think>\s*(.*)", re.DOTALL)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def normalized_snake_case(text: str) -> str:
    return casefy.snakecase(normalize(text))


def normalized_pascal_case(text: str) -> str:
    return casefy.pascalcase(normalize(text))


def parse_reasoning(text: str) -> tuple[str | None, str | None]:
    match = think_block_re.search(text)
    if match:
        think_block = match.group(1) or None
        msg = match.group(2).strip() or None
        return think_block, msg
    return None, text.strip() or None
