from unittest.mock import MagicMock, patch

from llm_tools.models import CharacterState
from llm_tools.parsers.markdown import extract_list, extract_section
from llm_tools.pipelines.memory import _extract_relationships, extract_character_state

SAMPLE_LLM_OUTPUT = """\
## Emotions
- Anxious
- Determined
- Conflicted

## Motivations
- Find her brother
- Prove herself worthy
- Protect the village

## Secrets
- Knows the king is her father
- Has the map hidden in her cloak

## Relationships
- Kael - ally - fought together at the gate
- Lord Vane - rival - competing for the throne
- Mira - friend - childhood companion

## Arc notes
She started the session hesitant but found resolve after the battle at the gate.

## Open threads
- Has not revealed the map to anyone
- The prophecy about the fallen king remains unexplained
"""


def test_extract_section():
    result = extract_section(SAMPLE_LLM_OUTPUT, "Arc notes")
    assert "hesitant" in result
    assert "resolve" in result


def test_extract_list():
    emotions = extract_list(SAMPLE_LLM_OUTPUT, "Emotions")
    assert "Anxious" in emotions
    assert "Determined" in emotions


def test_extract_relationships():
    rels = _extract_relationships(SAMPLE_LLM_OUTPUT)
    assert len(rels) == 3
    assert rels[0].character == "Kael"
    assert rels[0].type == "ally"
    assert rels[1].character == "Lord Vane"
    assert rels[1].type == "rival"


def test_extract_character_state_integration():
    from llm_tools.models import ChatSession, Turn

    session = ChatSession(
        source="test.jsonl",
        format="sillytavern",
        turns=[
            Turn(turn_id=1, prompt="Start the scene", response="She entered the room."),
            Turn(turn_id=2, prompt="Look around", response="Her eyes darted nervously."),
        ],
        character_name="Lunessa",
    )

    with patch("llm_tools.pipelines.memory.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm

        with patch("llm_tools.pipelines.memory.CHARACTER_MEMORY_PROMPT") as mock_prompt:
            mock_pipe = MagicMock()
            mock_pipe.__or__ = MagicMock(return_value=MagicMock())
            mock_pipe.__or__.return_value.invoke.return_value = SAMPLE_LLM_OUTPUT
            mock_prompt.__or__ = MagicMock(return_value=mock_pipe)

            state = extract_character_state(session)

    assert isinstance(state, CharacterState)
    assert state.name == "Lunessa"
    assert "Anxious" in state.emotions
    assert len(state.relationships) == 3
