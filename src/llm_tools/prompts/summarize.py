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
            "Write a memory chunk with sections:\n"
            "1) What happened (dense but readable)\n"
            "2) Character state (emotions, motivations, secrets)\n"
            "3) Open threads / hooks for next time\n"
            "4) Canon facts introduced (bullet list)\n",
        ),
    ]
)

REDUCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You combine multiple memory chunks into a cohesive session summary for retrieval-augmented generation.\n"
            "Keep it detailed, consistent, and non-redundant. Do not mention prompts.\n"
            "Prefer canonical facts and actionable hooks for continuing the story.",
        ),
        (
            "user",
            "Here are memory chunks from the session:\n\n{chunk_summaries}\n\n"
            "Produce the final session memory with:\n"
            "A) Narrative recap (multi-paragraph, not too short)\n"
            "B) Current character snapshot (goals, emotions, relationships, conflicts)\n"
            "C) World/canon facts (bullets)\n"
            "D) Continuation hooks (ranked list)\n"
            "E) Style/tone notes to maintain (bullets)\n",
        ),
    ]
)
