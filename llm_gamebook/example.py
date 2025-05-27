from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.location import Locations
from llm_gamebook.story.storyline import Storyline


def example_story_context() -> StoryContext:
    storyline = Storyline()
    beginning = storyline.create_node(
        "beginning",
        description="- Start of story\n- Player is depressed\n",
    )
    hope = storyline.create_node(
        "spark_of_hope",
        description=(
            "- Player found a faint spark of hope\n- Can he turn fate around and improve his miserable life?\n"
        ),
    )
    happy_end = storyline.create_node(
        "happy_end",
        description="- Player is happy\n- He gained new hope and will change his life to the better\n",
    )

    storyline.add_edge(beginning, hope)
    storyline.add_edge(hope, happy_end)

    locations = Locations()
    bedroom = locations.create_node(
        "bedroom",
        description="- dark, dim light\n- cockroaches under bed\n- musky smell\n",
    )

    living_room = locations.create_node(
        "living_room",
        description=(
            "- run-down, tiny appartment (living room with pantry kitchen, bedroom, bathroom)\n"
            "- messy, scattered with empty bottles\n"
            "- dim light\n"
            "- crumpled piece of paper under the front door (might have been placed there when player was sleeping)\n"
        ),
    )

    bathroom = locations.create_node(
        "bathroom",
        description="-broken bulp, dark\n- dripping faucet",
    )

    in_the_street = locations.create_node(
        "in_the_street",
        description="- nighttime, rainy, gloomy\n- empty save a drunkard talking to himself\n- flickering neon",
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
