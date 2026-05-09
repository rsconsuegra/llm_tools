from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from llm_tools.llm import create_llm
from llm_tools.models import CharacterRelationship, CharacterState, ChatSession
from llm_tools.parsers.markdown import extract_list, extract_section
from llm_tools.prompts.memory import CHARACTER_MEMORY_PROMPT


def extract_character_state(
    session: ChatSession,
    character_name: str | None = None,
    model: str | None = None,
    prompts: dict[str, ChatPromptTemplate] | None = None,
) -> CharacterState:
    name = character_name or session.character_name or "Miah"
    _prompt = (prompts or {}).get("memory") or CHARACTER_MEMORY_PROMPT
    llm = create_llm(model=model)
    chain = _prompt | llm | StrOutputParser()

    prompt_parts = [f"[Turn {t.turn_id}] {t.prompt}" for t in session.turns if t.prompt]

    character_text = "\n\n".join(t.response for t in session.turns).strip()
    prompt_context = "\n\n".join(prompt_parts).strip()

    output = chain.invoke({
        "character_name": name,
        "character_text": character_text,
        "prompt_context": prompt_context,
    })

    return CharacterState(
        name=name,
        emotions=extract_list(output, "Emotions"),
        motivations=extract_list(output, "Motivations"),
        secrets=extract_list(output, "Secrets"),
        relationships=_extract_relationships(output),
        arc_notes=extract_section(output, "Arc notes"),
        open_threads=extract_list(output, "Open threads"),
        source_turns=[t.turn_id for t in session.turns],
    )


def _extract_relationships(text: str) -> list[CharacterRelationship]:
    section = extract_section(text, "Relationships")
    relationships = []
    for line in section.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            stripped = stripped[2:].strip()
        if " - " in stripped:
            parts = stripped.split(" - ", maxsplit=2)
            if len(parts) >= 2:
                relationships.append(
                    CharacterRelationship(
                        character=parts[0].strip(),
                        type=parts[1].strip(),
                        notes=parts[2].strip() if len(parts) > 2 else None,
                    )
                )
    return relationships
