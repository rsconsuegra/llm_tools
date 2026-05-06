from langchain_core.prompts import ChatPromptTemplate

MAP_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are summarizing a creative roleplay/narrative session for future continuation.\n"
            "You will be given:\n"
            "A) Prompt context (what the user asked for)\n"
            "B) The character output (the story content)\n\n"
            "IMPORTANT:\n"
            "- Use the prompt context ONLY to interpret intent.\n"
            "- Do NOT summarize or include the prompt text as part of the memory.\n"
            "- Do NOT add turns info in the resume (like instructions of how to end the turns)\n"
            "- Summarize ONLY the narrative/story facts, character state, events, plans, relationships, tone.\n"
            "- Preserve names, places, unresolved threads, and decisions.\n",
        ),
        (
            "user",
            "PROMPT CONTEXT (do not summarize):\n{prompt_context}\n\n"
            "CHARACTER OUTPUT (summarize this):\n{character_text}\n\n"
            "Write a memory chunk with these sections:\n\n"
            "## What happened\n"
            "Dense narrative summary.\n\n"
            "## Character state\n"
            "Emotions, motivations, secrets, relationships, conflicts.\n\n"
            "## Open threads / hooks\n"
            "Bullet list.\n\n"
            "## Canon facts introduced\n"
            "Bullet list.\n",
        ),
    ]
)

COLLAPSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You compress several narrative memory chunks into one intermediate memory block.\n"
            "Preserve important canon facts, character state changes, and unresolved hooks.\n"
            "Remove repetition. Do not mention prompts or chunking.\n",
        ),
        (
            "user",
            "Memory chunks:\n\n{chunk_summaries}\n\n"
            "Create one consolidated intermediate memory block.",
        ),
    ]
)

REDUCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You combine multiple memory chunks into a cohesive session summary for retrieval-augmented generation.\n"
            "Keep it detailed, consistent, and non-redundant. Do not mention prompts.\n"
            "Prefer canonical facts and actionable hooks for continuing the story.\n",
        ),
        (
            "user",
            "Here are memory chunks from the session:\n\n{chunk_summaries}\n\n"
            "Produce the final session memory with:\n\n"
            "## Narrative recap\n"
            "Multi-paragraph, detailed but not bloated.\n\n"
            "## Current character snapshot\n"
            "Goals, emotions, relationships, conflicts, secrets.\n\n"
            "## World / canon facts\n"
            "Bullet list.\n\n"
            "## Continuation hooks\n"
            "Ranked bullet list.\n\n"
            "## Style / tone notes\n"
            "Bullet list.\n",
        ),
    ]
)
