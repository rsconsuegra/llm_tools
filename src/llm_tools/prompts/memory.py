from langchain_core.prompts import ChatPromptTemplate

CHARACTER_MEMORY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You extract character state from narrative text.\n"
            "Be precise, factual, and evidence-based. Do not invent traits not present in the text.\n"
            "Focus on observable state: emotions, motivations, secrets, relationships, and arc progression.\n",
        ),
        (
            "user",
            "CHARACTER: {character_name}\n\n"
            "PROMPT CONTEXT (for intent only, do not summarize):\n{prompt_context}\n\n"
            "CHARACTER OUTPUT (extract state from this):\n{character_text}\n\n"
            "Extract the current character state with these sections:\n\n"
            "## Emotions\n"
            "Current emotional state. Bullet list.\n\n"
            "## Motivations\n"
            "What drives them right now (wants, needs, goals). Bullet list.\n\n"
            "## Secrets\n"
            "Things the character knows but hasn't revealed. Bullet list.\n\n"
            "## Relationships\n"
            "One line per relationship: \"[other character] - [type] - [brief note]\".\n"
            "Use types: ally, rival, friend, enemy, mentor, love-interest, family, foil, confidant.\n\n"
            "## Arc notes\n"
            "How the character changed or developed in this session. Free text.\n\n"
            "## Open threads\n"
            "Unresolved character-specific threads. Bullet list.\n",
        ),
    ]
)
