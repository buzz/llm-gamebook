from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.location import LocationGraph
from llm_gamebook.story.storyline import Storyline


def example_story_context() -> StoryContext:
    storyline = Storyline()
    beginning = storyline.add_node(
        "beginning",
        description=("Start of story", "Player is depressed"),
    )
    hope = storyline.add_node(
        "spark_of_hope",
        description=(
            "Player found a faint spark of hope",
            "Can he turn fate around and improve his miserable life?",
        ),
    )
    happy_end = storyline.add_node(
        "happy_end",
        description=("Player is happy", "He gained new hope and will change his life to the better"),
    )

    storyline.add_edge(beginning, hope)
    storyline.add_edge(hope, happy_end)

    locations = LocationGraph()
    bedroom = locations.add_node(
        "bedroom",
        description=("dark, no light", "cockroaches under bed", "musky smell"),
    )

    living_room = locations.add_node(
        "living_room",
        description=(
            "run-down, tiny appartment (living room with pantry kitchen, bedroom, bathroom)",
            "messy, scattered with empty bottles",
            "dim light",
            "crumpled piece of paper under the door (player may choose to pick it up)",
        ),
    )

    bathroom = locations.add_node(
        "bathroom",
        description=("broken bulp, dark", "dripping faucet"),
    )

    in_the_street = locations.add_node(
        "in_the_street",
        description=("nighttime, rainy, gloomy", "empty save a drunkard talking to himself", "flickering neon"),
    )

    locations.add_edge(bedroom, living_room)
    locations.add_edge(living_room, bedroom)

    locations.add_edge(living_room, bathroom)
    locations.add_edge(bathroom, living_room)

    locations.add_edge(living_room, in_the_street)
    locations.add_edge(in_the_street, living_room)

    locations.current = bedroom
    storyline.current = beginning

    return StoryContext(storyline, locations)
