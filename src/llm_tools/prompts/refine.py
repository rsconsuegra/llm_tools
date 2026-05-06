from langchain_core.prompts import ChatPromptTemplate

REFINE_INITIAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are summarizing a creative narrative text (prologue, backstory, chapter, or scene).\n"
            "Produce a dense, faithful summary that preserves all story facts, character details,\n"
            "and world-building elements. Do not invent content. Do not add meta-commentary.\n",
        ),
        (
            "user",
            "{context_block}"
            "NARRATIVE TEXT:\n\n{text}\n\n"
            "Produce a summary with the following sections:\n"
            "1) What happens (dense narrative recap)\n"
            "2) Character state (identity, motivations, emotions, relationships)\n"
            "3) World/canon facts (bullet list)\n"
            "4) Open threads and unresolved elements\n",
        ),
    ]
)

REFINE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are refining a running summary of a creative narrative.\n"
            "Integrate new information without losing existing detail.\n"
            "Do not invent content. If the new text adds nothing useful, return the original summary.\n",
        ),
        (
            "user",
            "EXISTING SUMMARY:\n{existing_summary}\n\n"
            "NEW TEXT TO INTEGRATE:\n"
            "------------\n{text}\n"
            "------------\n\n"
            "Given the new text, refine the existing summary.\n"
            "Merge new facts, update character state, add new canon elements.\n"
            "If the new text isn't useful, return the original summary unchanged.\n",
        ),
    ]
)
