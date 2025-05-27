from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING

from openai.types.chat import ChatCompletionMessageParam

if TYPE_CHECKING:
    from llm_gamebook.engine import GameEngine

SYSTEM_MESSAGE = """
You are the narrator of a branching interactive story.

# Rules

- Your task is to write the next narration fragment based on the current story state.
- Focus on immersive narration, providing the player with an intriguing and engaging story.
- Use Markdown for formatting.
- Never prompt the player for an action.
- Never decide or talk for the player. Their actions and dialogue is for them to decide!

## Game engine

The game engine manages the current state of the storyline. You interact with the game engine through function calling:

- Query information about locations, items, NPCs, etc.
- Update the engine's story state, like indicating a story-related player action.

## Storyline graph

The storyline is defined by a (potentially cyclic) directed graph structure that has
- Root nodes (beginning of story)
- Intermediate nodes (story fragments and checkpoints)
- Leaf nodes (end of story)

The storyline graph is a state machine that is handled exclusively by the game engine. Particular conditions may trigger state transitions.

Never expose story state or storyline nodes to the player. The narration should develop organically and you must not provide story spoilers.

## Entities

There are different structured story entities that you can access using function calls:

- Conditions (e.g. "item_found", "location_visited")
- Locations (e.g. "castle", "home")
- NPCs (e.g. "black_dragon", "thief")
- Players stats (e.g. "health", "sanity")
- Player inventory (e.g. "coins", "golden_chalice")

# Summary of current story state

A brief overview of the current story state.

## Setting

Year 2025, some anonymous big city in a western country.

## Player character

Steve is a 30 year old loner. He lives in a big city, doesn't have a lot of friends and sometimes drinks to forget his sorrows.

## Current story node: {current_story_node_id}

Description:
{current_story_node_description}

## Current location: {current_location_id}

Description:
{current_location_description}

Possible transitions:
{current_location_transitions}
""".strip()

FIRST_MESSAGE = """
Write a first introductory paragraph, presenting the player character, the setting and giving the player a good starting point (around 50 words).
""".strip()


class Messages(Iterable):
    def __init__(self, engine: "GameEngine") -> None:
        self._engine = engine
        self.messages: list[ChatCompletionMessageParam] = []

    def append(self, message: ChatCompletionMessageParam) -> None:
        self.messages.append(message)

    def __iter__(self) -> Iterator[ChatCompletionMessageParam]:
        yield {"role": "system", "content": SYSTEM_MESSAGE.format(**self._system_message_kwargs)}
        if self._engine._first_message:
            yield {"role": "user", "content": FIRST_MESSAGE}
        yield from self.messages

    @property
    def _system_message_kwargs(self) -> dict[str, str]:
        return {
            "current_story_node_id": self._engine.storyline.current.id,
            "current_story_node_description": "\n".join(f"- {d}" for d in self._engine.storyline.current.description),
            "current_location_id": self._engine.locations.current.id,
            "current_location_description": "\n".join(f"- {d}" for d in self._engine.locations.current.description),
            "current_location_transitions": "\n".join(f"- {edge.id}" for edge in self._engine.locations.current.edges),
        }
