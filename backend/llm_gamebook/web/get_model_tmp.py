import json
from pathlib import Path

import httpx
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.logger import logger
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState


def _get_logging_http_client(timeout: float = 10.0, connect: float = 5.0) -> httpx.AsyncClient:
    async def log_request(request: httpx.Request) -> None:
        log = logger.getChild("http-request")
        if request.method.upper() == "POST":
            body = request.content
            try:
                body = json.loads(body)
            except ValueError:
                body_display = f"Couldn't decode json body: {body.decode()}"
            else:
                body_display = f"body:\n{json.dumps(body, indent=2)}"
            log.debug("POST %s body:\n%s", request.url, body_display)

    return httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=timeout, connect=connect),
        event_hooks={"request": [log_request]},
    )


def get_model_state() -> tuple[Model, StoryState]:
    path = Path(Path.home() / "llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
    state = StoryState(Project.from_path(path))

    api_key = "xxx"
    provider = OpenAIProvider(
        base_url="http://localhost:8888/v1",
        api_key=api_key,
        http_client=_get_logging_http_client(),
    )
    model = OpenAIChatModel("GLM-4.7", provider=provider)

    return model, state
