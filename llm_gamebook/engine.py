import contextlib
import json
import random
from collections.abc import Iterable

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionFunctionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)

from llm_gamebook.logger import logger
from llm_gamebook.messages import Messages
from llm_gamebook.story.location import LocationGraph
from llm_gamebook.story.state import StoryState
from llm_gamebook.story.storyline import Storyline


class GameEngine:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self._log = logger.getChild("engine")
        self.state = StoryState()
        self._messages = Messages(self)
        self.storyline = Storyline()
        self.locations = LocationGraph()
        self._user_input: str = ""
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key or "dummy")
        self._first_message = True

    def example(self) -> None:
        beginning = self.storyline.add_node(
            "beginning",
            description=("Start of story", "Player is depressed"),
        )
        hope = self.storyline.add_node(
            "spark_of_hope",
            description=(
                "Player found a faint spark of hope",
                "Can he turn fate around and improve his miserable life?",
            ),
        )
        happy_end = self.storyline.add_node(
            "happy_end",
            description=("Player is happy", "He gained new hope and will change his life to the better"),
        )

        self.storyline.add_edge(beginning, hope)
        self.storyline.add_edge(hope, happy_end)

        bedroom = self.locations.add_node(
            "bedroom",
            description=("dark, no light", "cockroaches under bed", "musky smell"),
        )

        living_room = self.locations.add_node(
            "living_room",
            description=(
                "run-down, tiny appartment (living room with pantry kitchen, bedroom, bathroom)",
                "messy, scattered with empty bottles",
                "dim light",
                "crumpled piece of paper under the door (player may choose to pick it up)",
            ),
        )

        bathroom = self.locations.add_node(
            "bathroom",
            description=("broken bulp, dark", "dripping faucet"),
        )

        in_the_street = self.locations.add_node(
            "in_the_street",
            description=("nighttime, rainy, gloomy", "empty save a drunkard talking to himself", "flickering neon"),
        )

        self.locations.add_edge(bedroom, living_room)
        self.locations.add_edge(living_room, bedroom)

        self.locations.add_edge(living_room, bathroom)
        self.locations.add_edge(bathroom, living_room)

        self.locations.add_edge(living_room, in_the_street)
        self.locations.add_edge(in_the_street, living_room)

        self.locations.current = bedroom
        self.storyline.current = beginning

    async def game_loop(self) -> None:
        while self._user_input != "quit":
            self._log.debug("**********************************************************")
            self._log.debug("Current messages:")
            for msg_ in self._messages:
                role = msg_["role"]
                if role == "assistant":
                    content = list(msg_["tool_calls"])
                    self._log.debug(f"- {role}: {content}")
                else:
                    content = msg_["content"]
                    self._log.debug(f"- {role}: {content}")

            kwargs = {
                "model": "openai/models/gguf/Qwen3-32B-Q4_K_M.gguf",
                "messages": self._messages,
                "seed": random.randint(0, 99999),
                "max_tokens": 2048,
                "max_completion_tokens": 512,
            }

            if not self._first_message:
                kwargs["tools"] = None if self._first_message else self._tools
                kwargs["tool_choice"] = "auto"

            response = await self._client.chat.completions.create(**kwargs)
            self._first_message = False

            message = response.choices[0].message

            with contextlib.suppress(AttributeError):
                self._log.debug("Reasoning: %s", message.reasoning_content)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    self._messages.append(
                        ChatCompletionAssistantMessageParam(
                            role="assistant",
                            content=message.content,
                            tool_calls=(
                                ChatCompletionMessageToolCallParam(
                                    id=tc.id,
                                    function={"name": tc.function.name, "arguments": tc.function.arguments},
                                    type=tc.type,
                                )
                                for tc in message.tool_calls
                            ),
                        ),
                    )

                    if tool_call.function.name == "change_location":
                        self._log.debug(
                            "Got tool call: %s args=%s",
                            tool_call.function.name,
                            tool_call.function.arguments,
                        )
                        args = json.loads(tool_call.function.arguments)
                        location_id = args["location"]
                        self.locations.current = self.locations.nodes[location_id]

                        self._messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"result": "success"}),
                        })

            elif message.content:
                print(f"\nNARRATOR:\n{message.content.strip()}\n")
                self._user_input = input("> ")
                self._messages.append(ChatCompletionUserMessageParam(role="user", content=self._user_input))

            else:
                msg = "No tool call or content message received."
                self._log.error(f"{msg} Last message: %s", message)
                raise RuntimeError(msg)

    @property
    def _tools(self) -> Iterable[ChatCompletionToolParam]:
        yield from self.locations.function_params
