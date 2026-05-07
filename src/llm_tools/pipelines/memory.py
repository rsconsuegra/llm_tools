from langchain_core.output_parsers import StrOutputParser

from llm_tools.llm import create_llm
from llm_tools.models import CharacterState, ChatSession
from llm_tools.prompts.memory import CHARACTER_MEMORY_PROMPT


def extract_character_state(
    session: ChatSession,
    character_name: str | None = None,
    model: str | None = None,
) -> CharacterState:
    name = character_name or session.character_name or "Miah"
    llm = create_llm(model=model)
    chain = CHARACTER_MEMORY_PROMPT | llm | StrOutputParser()

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
        emotions=_extract_list(output, "Emotions"),
        motivations=_extract_list(output, "Motivations"),
        secrets=_extract_list(output, "Secrets"),
        relationships=_extract_relationships(output),
        arc_notes=_extract_section(output, "Arc notes"),
        open_threads=_extract_list(output, "Open threads"),
        source_turns=[t.turn_id for t in session.turns],
    )


def _extract_section(text: str, header: str) -> str:
    lines = text.split("\n")
    capturing = False
    result: list[str] = []

    for line in lines:
        if line.strip().startswith(f"## {header}"):
            capturing = True
            continue
        if capturing and line.strip().startswith("## "):
            break
        if capturing:
            result.append(line)

    return "\n".join(result).strip()


def _extract_list(text: str, header: str) -> list[str]:
    section = _extract_section(text, header)
    items = []
    for line in section.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            items.append(stripped[2:].strip())
        elif stripped and not stripped.startswith("#"):
            items.append(stripped)
    return items


def _extract_relationships(text: str) -> list:
    from llm_tools.models import CharacterRelationship

    section = _extract_section(text, "Relationships")
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
