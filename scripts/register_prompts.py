"""Register all local prompt templates in Agenta.

Usage:
    AGENTA_HOST=http://192.168.1.6:9091 \
    AGENTA_API_KEY=your-key \
    uv run python scripts/register_prompts.py
"""

import agenta as ag

VARIANT_SLUG = "default"
ENVIRONMENT = "production"

PROMPTS = {
    "summarize-map": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are summarizing a creative roleplay/narrative session for future continuation.\n"
                    "You will be given:\n"
                    "A) Prompt context (what the user asked for)\n"
                    "B) The character output (the story content)\n\n"
                    "IMPORTANT:\n"
                    "- Use the prompt context ONLY to interpret intent.\n"
                    "- Do NOT summarize or include the prompt text as part of the memory.\n"
                    "- Do NOT add turns info in the resume (like instructions of how to end the turns)\n"
                    "- Summarize ONLY the narrative/story facts, character state, events, plans, relationships, tone.\n"
                    "- Preserve names, places, unresolved threads, and decisions.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "PROMPT CONTEXT (do not summarize):\n{{prompt_context}}\n\n"
                    "CHARACTER OUTPUT (summarize this):\n{{character_text}}\n\n"
                    "Write a memory chunk with these sections:\n\n"
                    "## What happened\n"
                    "Dense narrative summary.\n\n"
                    "## Character state\n"
                    "Emotions, motivations, secrets, relationships, conflicts.\n\n"
                    "## Open threads / hooks\n"
                    "Bullet list.\n\n"
                    "## Canon facts introduced\n"
                    "Bullet list.\n"
                ),
            },
        ],
    },
    "summarize-collapse": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You compress several narrative memory chunks into one intermediate memory block.\n"
                    "Preserve important canon facts, character state changes, and unresolved hooks.\n"
                    "Remove repetition. Do not mention prompts or chunking.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Memory chunks:\n\n{{chunk_summaries}}\n\n"
                    "Create one consolidated intermediate memory block."
                ),
            },
        ],
    },
    "summarize-reduce": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You combine multiple memory chunks into a cohesive session summary for "
                    "retrieval-augmented generation.\n"
                    "Keep it detailed, consistent, and non-redundant. Do not mention prompts.\n"
                    "Prefer canonical facts and actionable hooks for continuing the story.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Here are memory chunks from the session:\n\n{{chunk_summaries}}\n\n"
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
                    "Bullet list.\n"
                ),
            },
        ],
    },
    "refine-initial": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are summarizing a creative narrative text (prologue, backstory, chapter, or scene).\n"
                    "Produce a dense, faithful summary that preserves all story facts, character details,\n"
                    "and world-building elements. Do not invent content. Do not add meta-commentary.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "{{context_block}}"
                    "NARRATIVE TEXT:\n\n{{text}}\n\n"
                    "Produce a summary with these sections:\n\n"
                    "## What happens\n"
                    "Dense narrative recap.\n\n"
                    "## Character state\n"
                    "Identity, motivations, emotions, relationships.\n\n"
                    "## World / canon facts\n"
                    "Bullet list.\n\n"
                    "## Open threads\n"
                    "Bullet list of unresolved elements.\n"
                ),
            },
        ],
    },
    "refine": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are refining a running summary of a creative narrative.\n"
                    "Integrate new information without losing existing detail.\n"
                    "Do not invent content. If the new text adds nothing useful, "
                    "return the original summary.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "EXISTING SUMMARY:\n{{existing_summary}}\n\n"
                    "NEW TEXT TO INTEGRATE:\n"
                    "------------\n{{text}}\n"
                    "------------\n\n"
                    "Given the new text, refine the existing summary.\n"
                    "Merge new facts, update character state, add new canon elements.\n"
                    "If the new text isn't useful, return the original summary unchanged.\n"
                ),
            },
        ],
    },
    "memory": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract character state from narrative text.\n"
                    "Be precise, factual, and evidence-based. "
                    "Do not invent traits not present in the text.\n"
                    "Focus on observable state: emotions, motivations, secrets, "
                    "relationships, and arc progression.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "CHARACTER: {{character_name}}\n\n"
                    "PROMPT CONTEXT (for intent only, do not summarize):\n{{prompt_context}}\n\n"
                    "CHARACTER OUTPUT (extract state from this):\n{{character_text}}\n\n"
                    "Extract the current character state with these sections:\n\n"
                    "## Emotions\n"
                    "Current emotional state. Bullet list.\n\n"
                    "## Motivations\n"
                    "What drives them right now (wants, needs, goals). Bullet list.\n\n"
                    "## Secrets\n"
                    "Things the character knows but hasn't revealed. Bullet list.\n\n"
                    "## Relationships\n"
                    'One line per relationship: "[other character] - [type] - [brief note]".\n'
                    "Use types: ally, rival, friend, enemy, mentor, love-interest, "
                    "family, foil, confidant.\n\n"
                    "## Arc notes\n"
                    "How the character changed or developed in this session. Free text.\n\n"
                    "## Open threads\n"
                    "Unresolved character-specific threads. Bullet list.\n"
                ),
            },
        ],
    },
    "consistency": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a narrative consistency auditor.\n"
                    "Check the content against the provided norms/rules.\n"
                    "Be specific: quote the problematic text, explain why it violates a rule, "
                    "suggest a fix.\n"
                    "Do not be nitpicky — only flag genuine issues.\n"
                    "If the content fully complies with all norms, say so explicitly.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "NORMS/RULES:\n{{norms}}\n\n"
                    "CONTENT TO CHECK:\n{{content}}\n\n"
                    "Produce a consistency report with these sections:\n\n"
                    "## Violations\n"
                    "Clear rule breaks. For each: quote the text, name the violated rule, "
                    "suggest a fix.\n\n"
                    "## Warnings\n"
                    "Questionable but not definitive violations. For each: quote the text, "
                    "explain the concern.\n\n"
                    "## Observations\n"
                    "Things worth noting that don't break rules but may need attention.\n\n"
                    "## Overall assessment\n"
                    "One-paragraph summary of compliance status.\n"
                ),
            },
        ],
    },
    "character-design": {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You design detailed fictional characters from rough concepts.\n"
                    "Be specific and vivid. Avoid generic traits. "
                    "Every detail should suggest story potential.\n"
                    "If the concept is thin, invent details that create internal contradiction "
                    "and narrative tension.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "CONCEPT: {{concept}}\n\n"
                    "Expand this concept into a full character profile with these sections:\n\n"
                    "## Name\n"
                    "Full name and any aliases.\n\n"
                    "## Role\n"
                    "protagonist / antagonist / supporting / minor\n\n"
                    "## Age\n"
                    "Approximate age or age range.\n\n"
                    "## Appearance\n"
                    "Build, distinguishing features, how they carry themselves. "
                    'Be specific \u2014 not "tall and beautiful" but details that reveal character.\n\n'
                    "## Personality\n"
                    "Core traits, temperament, habits, quirks. Include at least one contradictory pair "
                    "(e.g., generous but vindictive). What makes them memorable in a scene?\n\n"
                    "## Backstory\n"
                    "Formative events only. What shaped who they are? "
                    "Skip encyclopedia biography.\n\n"
                    "## Motivations\n"
                    "External want vs internal need. These must conflict. "
                    'Format: "Wants [X] but needs [Y]."\n\n'
                    "## Voice\n"
                    "Vocabulary level, sentence length, verbal tics, tone. "
                    "Include 2-3 lines of example dialogue.\n\n"
                    "## Arc\n"
                    "Starting state \u2192 key turning point(s) \u2192 projected end state.\n"
                ),
            },
        ],
    },
}


def build_parameters(messages: list[dict]) -> dict:
    return {
        "prompt": {
            "messages": messages,
            "template_format": "curly",
            "llm_config": {
                "model": "nousresearch/hermes-3-llama-3.1-405b:free",
                "temperature": 0.0,
                "max_tokens": 4096,
            },
        }
    }


def main():
    ag.init()

    existing = ag.AppManager.list()
    existing_slugs = {app.app_slug for app in existing} if existing else set()

    for app_slug, prompt_data in PROMPTS.items():
        params = build_parameters(prompt_data["messages"])
        is_new = app_slug not in existing_slugs

        if is_new:
            try:
                ag.AppManager.create(app_slug=app_slug, template_key="SERVICE:chat")
                print(f"[APP]  Created {app_slug}")
            except Exception as e:
                print(f"[ERR]  Failed to create app {app_slug}: {e}")
                continue

        try:
            variants = ag.VariantManager.list(app_slug=app_slug)
            variant_slug = variants[0].variant_slug if variants else app_slug.replace("-", "")

            if not variants:
                ag.VariantManager.create(
                    parameters=params,
                    variant_slug=variant_slug,
                    app_slug=app_slug,
                )
                print(f"[VAR]  Created variant '{variant_slug}' for {app_slug}")
            else:
                ag.VariantManager.commit(
                    parameters=params,
                    variant_slug=variant_slug,
                    app_slug=app_slug,
                )
                print(f"[VAR]  Updated variant '{variant_slug}' for {app_slug}")
        except Exception as e:
            print(f"[ERR]  Failed to set variant for {app_slug}: {e}")
            continue

        try:
            ag.DeploymentManager.deploy(
                variant_slug=variant_slug,
                environment_slug=ENVIRONMENT,
                app_slug=app_slug,
            )
            print(f"[DEP]  Deployed {app_slug} to {ENVIRONMENT}")
        except Exception as e:
            print(f"[WARN] Failed to deploy {app_slug}: {e}")

    print("\nDone. Registered prompts:")
    for slug in PROMPTS:
        status = "registered" if slug not in existing_slugs else "existed"
        print(f"  {slug}: {status}")


if __name__ == "__main__":
    main()
