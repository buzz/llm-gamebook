from llm_gamebook.story.condition import IsCurrentLocationCondition
from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.location import Locations
from llm_gamebook.story.story_arc import StoryArc


def example_story_context() -> StoryContext:
    main_arc = StoryArc("Main")
    beginning = main_arc.create_node(
        "The Beginning",
        description="- Start of story\n- Player is depressed\n",
    )
    hope = main_arc.create_node(
        "Spark of Hope",
        description=(
            "- Player found a faint spark of hope\n"
            "- Can he turn fate around and improve his miserable life?\n"
        ),
    )
    happy_end = main_arc.create_node(
        "Happy End",
        description=(
            "- Player is happy\n- He gained new hope and will change his life to the better\n"
        ),
    )

    main_arc.add_edge(beginning, hope)
    main_arc.add_edge(hope, happy_end)
    main_arc.current = beginning

    community_center_arc = StoryArc("The Leaflet")
    leaflet_not_found = community_center_arc.create_node(
        "Leaflet not found yet",
        description=(
            "- A leaflet was placed under the player's front door."
            "\n- Its content is not yet revealed."
        ),
    )
    found = community_center_arc.create_node(
        "Leaftlet found",
        description=(
            "- Player found the leaflet\n"
            "- It's an invitation to a meeting at the local community center."
        ),
    )
    attending_meeting = community_center_arc.create_node(
        "Attending meeting",
        description=(
            "- Player found a leaflet with an invitation to "
            "a meeting at the local community center.\n"
            "- Player is attending the meeting."
        ),
    )
    meeting_is_over = community_center_arc.create_node(
        "Meeting is over",
        description=(
            "- Player found a leaflet with an invitation to "
            "a meeting at the local community center.\n"
            "- The player attended and the meeting is over."
        ),
    )

    community_center_arc.add_edge(leaflet_not_found, found)
    community_center_arc.add_edge(found, attending_meeting)
    community_center_arc.add_edge(attending_meeting, meeting_is_over)
    community_center_arc.current = leaflet_not_found

    locations = Locations("Locations")
    bedroom = locations.create_node(
        "Bedroom",
        description="- dark, dim light\n- cockroaches under bed\n- musky smell\n",
    )

    living_room = locations.create_node(
        "Living room",
        description=(
            "- run-down, tiny appartment (living room with pantry kitchen, bedroom, bathroom)\n"
            "- messy, scattered with empty bottles\n"
            "- dim light\n"
            "- crumpled piece of paper under the front door "
            "(might have been placed there when player was sleeping)\n"
        ),
    )

    bathroom = locations.create_node(
        "Bathroom",
        description="-broken bulp, dark\n- dripping faucet",
    )

    in_the_street = locations.create_node(
        "In the street",
        description=(
            "- nighttime, rainy, gloomy\n"
            "- empty save a drunkard talking to himself\n"
            "- flickering neon"
        ),
    )

    community_center = locations.create_node(
        "Community center",
        description=(
            "- luxurious interior\n"
            "- grotesquely happy people that warmly invite the player inside\n"
            "- some weird subtle vibe that's hard to place, almost an "
            "aggression can be felt despite the happy faces"
        ),
    )

    locations.add_edge(bedroom, living_room)
    locations.add_edge(living_room, bedroom)

    locations.add_edge(living_room, bathroom)
    locations.add_edge(bathroom, living_room)

    locations.add_edge(living_room, in_the_street)
    locations.add_edge(in_the_street, living_room)

    locations.add_edge(in_the_street, community_center)
    locations.add_edge(community_center, in_the_street)

    locations.current = bedroom

    community_center_arc.conditions.append(
        IsCurrentLocationCondition("Is in living room", living_room, locations),
    )

    return StoryContext([main_arc, community_center_arc], locations)
