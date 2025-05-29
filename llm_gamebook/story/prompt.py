from typing import TYPE_CHECKING

from jinja2 import Environment, PackageLoader

if TYPE_CHECKING:
    from llm_gamebook.story.state import StoryState


class PromptGenerator:
    def __init__(self, state: "StoryState") -> None:
        self._state = state
        self._jinja_env = Environment(
            loader=PackageLoader(__name__, "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )

    async def get(self) -> str:
        ctx = self._get_template_context()
        return await self._jinja_env.get_template("system_prompt.md.jinja2").render_async(ctx)

    def _get_template_context(self) -> dict[str, object]:
        return {
            "title": self._state.title,
            "description": self._state.description,
            "entity_types": [et.get_template_context() for et in self._state.entity_types.values()],
            # "setting": self.setting,
            # "player_char": self.player_char,
            # "story_arcs": [arc for arc in self.story_arcs if arc.is_enabled()],
            # "location": self.locations.current,
            # "reachable_locations": self.locations.current.edges,
        }

    async def get_first_message(self) -> str:
        return await self._jinja_env.get_template("first_message.md.jinja2").render_async()
