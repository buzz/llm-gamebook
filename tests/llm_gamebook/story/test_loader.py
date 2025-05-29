from pathlib import Path

from llm_gamebook.story.loader import YAMLLoader


def test_yaml_loader(examples_path: Path) -> None:
    context = YAMLLoader(examples_path / "broken-bulb").load()
    assert len(context.entity_types) == 4
