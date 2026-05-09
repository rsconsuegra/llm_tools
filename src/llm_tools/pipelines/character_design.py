from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from llm_tools.llm import create_llm
from llm_tools.models import CharacterDesign
from llm_tools.parsers.markdown import extract_section
from llm_tools.prompts.character_design import CHARACTER_DESIGN_PROMPT


def generate_character(
    concept: str,
    model: str | None = None,
    prompts: dict[str, ChatPromptTemplate] | None = None,
) -> CharacterDesign:
    _prompt = (prompts or {}).get("character-design") or CHARACTER_DESIGN_PROMPT
    llm = create_llm(model=model)
    chain = _prompt | llm | StrOutputParser()
    output = chain.invoke({"concept": concept})

    name_raw = extract_section(output, "Name")
    role_raw = extract_section(output, "Role")
    age_raw = extract_section(output, "Age")

    aliases = []
    if "aka" in name_raw.lower() or "(" in name_raw:
        base = name_raw.split("(")[0].split("aka")[0].strip()
        for part in name_raw.replace(")", "(").split("(")[1:]:
            cleaned = part.strip().strip(",").removeprefix("aka").strip()
            if cleaned:
                aliases.append(cleaned)
    else:
        base = name_raw.strip()

    return CharacterDesign(
        name=base or "Unnamed",
        role=_first_line(role_raw).lower(),
        age=_first_line(age_raw),
        appearance=extract_section(output, "Appearance"),
        personality=extract_section(output, "Personality"),
        backstory=extract_section(output, "Backstory"),
        motivations=extract_section(output, "Motivations"),
        voice=extract_section(output, "Voice"),
        arc=extract_section(output, "Arc"),
        aliases=aliases,
    )


def _first_line(text: str) -> str:
    return text.split("\n")[0].strip() if text else ""
