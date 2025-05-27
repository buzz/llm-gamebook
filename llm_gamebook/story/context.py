from jinja2 import Environment, PackageLoader

from llm_gamebook.story.location import Locations
from llm_gamebook.story.storyline import Storyline
from llm_gamebook.types import StoryTool


class StoryContext:
    def __init__(self, storyline: Storyline, locations: Locations) -> None:
        self.storyline = storyline
        self.locations = locations
        self.setting = "The year is 2025. A nameless, sprawling metropolis in the Western world."
        self.player_char = (
            "Steve, 30 years old, isolated and weary. "
            "He lives alone in the city, struggling with loneliness and often drinks to numb his thoughts."
        )

        self._jinja_env = Environment(
            loader=PackageLoader(__name__, "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )

    async def get_system_prompt(self) -> str:
        template_ctx = {
            "setting": self.setting,
            "player_char": self.player_char,
            "current_story_node_id": self.storyline.current.id,
            "current_story_node_description": self.storyline.current.description,
            "current_location_id": self.locations.current.id,
            "current_location_description": self.locations.current.description,
            "current_location_transitions": self.locations.current.edges,
        }
        return await self._jinja_env.get_template("system_prompt.md.jinja2").render_async(template_ctx)

    async def get_first_message(self) -> str:
        return await self._jinja_env.get_template("first_message.md").render_async()

    @property
    def tools(self) -> list[StoryTool]:
        return list(self.storyline.tools) + list(self.locations.tools)
