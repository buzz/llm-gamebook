import pytest

from llm_gamebook.story.conditions.evaluator import BoolExprEvaluator
from llm_gamebook.story.project import Project


@pytest.fixture
def evaluator(simple_project: Project) -> BoolExprEvaluator:
    return BoolExprEvaluator(simple_project)
