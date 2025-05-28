from collections.abc import Mapping, Sequence

from jinja2 import Environment, PackageLoader

from llm_gamebook.story.location import Locations
from llm_gamebook.story.story_arc import StoryArc
from llm_gamebook.types import StoryTool


class StoryContext:
    def __init__(self, story_arcs: Sequence[StoryArc], locations: Locations) -> None:
        self.story_arcs = story_arcs
        self.locations = locations
        self.setting = "The year is 2025. A nameless, sprawling metropolis in the Western world."
        self.player_char = (
            "Steve, 30 years old, isolated and weary. "
            "He lives alone in the city, struggling with loneliness and "
            "often drinks to numb his thoughts."
        )

        self._jinja_env = Environment(
            loader=PackageLoader(__name__, "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )

    async def get_system_prompt(self) -> str:
        ctx = self._get_system_prompt_context()
        return await self._jinja_env.get_template("system_prompt.md.jinja2").render_async(ctx)

    def _get_system_prompt_context(self) -> Mapping[str, object]:
        return {
            "setting": self.setting,
            "player_char": self.player_char,
            "story_arcs": [arc for arc in self.story_arcs if arc.is_enabled()],
            "location": self.locations.current,
            "reachable_locations": self.locations.current.edges,
        }

    async def get_first_message(self) -> str:
        return await self._jinja_env.get_template("first_message.md").render_async()

    @property
    def tools(self) -> list[StoryTool]:
        return list(self.locations.tools)
