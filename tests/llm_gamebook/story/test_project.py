from pathlib import Path

from llm_gamebook.story.project import Project
from llm_gamebook.story.traits.graph import GraphNodeTrait


def test_project_from_dir(examples_path: Path) -> None:
    project = Project.from_dir(examples_path / "broken-bulb")
    assert len(project.entity_types) == 4

    assert project.entity_type_map["StoryArc"].name == "Story Arc"

    location_type = project.entity_type_map["Location"]
    bedroom = location_type.get_entity("bedroom", GraphNodeTrait)
    living_room = location_type.get_entity("living_room", GraphNodeTrait)
    assert bedroom.edges == [living_room]
