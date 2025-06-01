from pathlib import Path

from llm_gamebook.story.project import Project
from llm_gamebook.story.traits.described import DescribedTrait
from llm_gamebook.story.traits.graph import GraphTrait


def test_evaluator(examples_path: Path) -> None:
    project = Project.from_dir(examples_path / "broken-bulb")
    leaflet_not_found_yet = project.get_entity("leaflet_not_found_yet", DescribedTrait)
    locations = project.get_entity("locations", GraphTrait)

    assert not leaflet_not_found_yet.enabled.evaluate(project)
    locations.transition("living_room")
    assert leaflet_not_found_yet.enabled.evaluate(project)
