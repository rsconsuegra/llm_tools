from unittest.mock import MagicMock, patch

from llm_tools.models import CharacterDesign
from llm_tools.pipelines.character_design import generate_character

SAMPLE_LLM_OUTPUT = """\
## Name
Seraya Voss (aka The Ashen Blade)

## Role
protagonist

## Age
27

## Appearance
Lean and angular, with burn scars climbing her left arm. Moves like she expects
every room to have an exit she can't find. Wears practical dark leather, always
with sleeves long enough to cover the scars. Has a habit of cracking her knuckles
when she's thinking.

## Personality
Calculating, intensely loyal to the few people she trusts, and pathologically
unable to accept help. Generous with money but vindictive toward perceived slights.
Talks to her horse more honestly than to any person.

## Backstory
Her village was burned during the Siege of Holn when she was twelve. She survived
by hiding in the ash pile for three days. Joined a mercenary company at fifteen,
rose to second-in-command, then left when the captain ordered a massacre she refused
to carry out.

## Motivations
Wants to find the commander who ordered the siege of Holn and kill him, but needs
to stop defining herself through that day and let herself build something new.

## Voice
Short, clipped sentences. Military vocabulary. Tends to answer questions with
questions when she doesn't want to engage.

Example dialogue:
- "You asking because you care, or because you need something?"
- "Orders are orders. Doesn't mean I have to like the taste."
- "I don't need backup. I need a door that opens outward."

## Arc
Starts as someone who sees every relationship as transactional. After being forced
to rely on an ally during the attack on Kessel Ridge, she begins to accept that
vulnerability isn't weakness. Projected end: she lets the commander live and
chooses to protect what she's built instead of destroying what she's lost.
"""


def test_generate_character_parsing():
    with patch("llm_tools.pipelines.character_design.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm

        with patch("llm_tools.pipelines.character_design.CHARACTER_DESIGN_PROMPT") as mock_prompt:
            mock_pipe = MagicMock()
            mock_pipe.__or__ = MagicMock(return_value=MagicMock())
            mock_pipe.__or__.return_value.invoke.return_value = SAMPLE_LLM_OUTPUT
            mock_prompt.__or__ = MagicMock(return_value=mock_pipe)

            design = generate_character("A burned mercenary seeking revenge")

    assert isinstance(design, CharacterDesign)
    assert design.name == "Seraya Voss"
    assert design.role == "protagonist"
    assert design.age == "27"
    assert "burn scars" in design.appearance.lower()
    assert "calculating" in design.personality.lower()
    assert "siege of holn" in design.backstory.lower()
    assert "wants" in design.motivations.lower() and "needs" in design.motivations.lower()
    assert "example dialogue" in design.voice.lower()
    assert "transactional" in design.arc.lower()
    assert "The Ashen Blade" in design.aliases


def test_generate_character_minimal_output():
    minimal_output = """\
## Name
Kai

## Role
supporting

## Age
Unknown

## Appearance
Short, wiry, quick movements.

## Personality
Curious, restless, impatient with authority.

## Backstory
Grew up on the streets of the capital. No formal education.

## Motivations
Wants to prove he's more than a street rat but needs to accept help from others.

## Voice
Casual, slang-heavy, often sarcastic.

## Arc
Starts as a lone survivor. Learns to trust a group. Ends as a team player.
"""

    with patch("llm_tools.pipelines.character_design.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm

        with patch("llm_tools.pipelines.character_design.CHARACTER_DESIGN_PROMPT") as mock_prompt:
            mock_pipe = MagicMock()
            mock_pipe.__or__ = MagicMock(return_value=MagicMock())
            mock_pipe.__or__.return_value.invoke.return_value = minimal_output
            mock_prompt.__or__ = MagicMock(return_value=mock_pipe)

            design = generate_character("A street kid")

    assert design.name == "Kai"
    assert design.role == "supporting"
    assert design.aliases == []
