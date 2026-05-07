from langchain_core.prompts import ChatPromptTemplate

CHARACTER_DESIGN_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You design detailed fictional characters from rough concepts.\n"
            "Be specific and vivid. Avoid generic traits. Every detail should suggest story potential.\n"
            "If the concept is thin, invent details that create internal contradiction and narrative tension.\n",
        ),
        (
            "user",
            "CONCEPT: {concept}\n\n"
            "Expand this concept into a full character profile with these sections:\n\n"
            "## Name\n"
            "Full name and any aliases.\n\n"
            "## Role\n"
            "protagonist / antagonist / supporting / minor\n\n"
            "## Age\n"
            "Approximate age or age range.\n\n"
            "## Appearance\n"
            "Build, distinguishing features, how they carry themselves. "
            "Be specific — not \"tall and beautiful\" but details that reveal character.\n\n"
            "## Personality\n"
            "Core traits, temperament, habits, quirks. Include at least one contradictory pair "
            "(e.g., generous but vindictive). What makes them memorable in a scene?\n\n"
            "## Backstory\n"
            "Formative events only. What shaped who they are? Skip encyclopedia biography.\n\n"
            "## Motivations\n"
            "External want vs internal need. These must conflict. "
            "Format: \"Wants [X] but needs [Y].\"\n\n"
            "## Voice\n"
            "Vocabulary level, sentence length, verbal tics, tone. "
            "Include 2-3 lines of example dialogue.\n\n"
            "## Arc\n"
            "Starting state → key turning point(s) → projected end state.\n",
        ),
    ]
)
