from langchain_core.prompts import ChatPromptTemplate

CONSISTENCY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a narrative consistency auditor.\n"
            "Check the content against the provided norms/rules.\n"
            "Be specific: quote the problematic text, explain why it violates a rule, suggest a fix.\n"
            "Do not be nitpicky — only flag genuine issues.\n"
            "If the content fully complies with all norms, say so explicitly.\n",
        ),
        (
            "user",
            "NORMS/RULES:\n{norms}\n\n"
            "CONTENT TO CHECK:\n{content}\n\n"
            "Produce a consistency report with these sections:\n\n"
            "## Violations\n"
            "Clear rule breaks. For each: quote the text, name the violated rule, suggest a fix.\n\n"
            "## Warnings\n"
            "Questionable but not definitive violations. For each: quote the text, explain the concern.\n\n"
            "## Observations\n"
            "Things worth noting that don't break rules but may need attention.\n\n"
            "## Overall assessment\n"
            "One-paragraph summary of compliance status.\n",
        ),
    ]
)
