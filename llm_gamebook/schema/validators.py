import re
from typing import Any

from llm_gamebook.utils import slugify


def is_slug(v: str) -> str:
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    if not re.match(pattern, v):
        msg = "Invalid slug format"
        raise ValueError(msg)
    return v


def derive_from_name(v: Any) -> Any:
    if isinstance(v, dict):
        try:
            name = v["name"]
        except KeyError:
            pass
        else:
            if "slug" not in v:
                v["slug"] = slugify(name)
    return v
