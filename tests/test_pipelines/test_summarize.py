from llm_tools.models import ChatSession, Turn
from llm_tools.pipelines.summarize import _group_turns, _turns_to_docs


def test_group_turns_default_chunk():
    turns = [Turn(turn_id=i, prompt=f"p{i}", response=f"r{i}") for i in range(1, 9)]
    session = ChatSession(source="test", format="test", turns=turns)

    groups = _group_turns(session, turns_per_chunk=4)
    assert len(groups) == 2
    assert len(groups[0]) == 4
    assert len(groups[1]) == 4


def test_group_turns_remainder():
    turns = [Turn(turn_id=i, prompt=f"p{i}", response=f"r{i}") for i in range(1, 7)]
    session = ChatSession(source="test", format="test", turns=turns)

    groups = _group_turns(session, turns_per_chunk=4)
    assert len(groups) == 2
    assert len(groups[0]) == 4
    assert len(groups[1]) == 2


def test_turns_to_docs():
    turns = [
        Turn(turn_id=1, prompt="Go north", response="The path winds."),
        Turn(turn_id=2, prompt="Look around", response="Trees everywhere."),
    ]
    groups = [turns]
    docs = _turns_to_docs(groups)

    assert len(docs) == 1
    assert docs[0].metadata["chunk_id"] == 1
    assert docs[0].metadata["turn_ids"] == [1, 2]
    assert "path winds" in docs[0].page_content
    assert "Go north" in docs[0].metadata["prompt_context"]
