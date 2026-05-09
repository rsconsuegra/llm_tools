import logging

import agenta as ag
from langchain_core.prompts import ChatPromptTemplate

from llm_tools.config import AGENTA_ENABLED

logger = logging.getLogger(__name__)

_instrumented = False


def init_agenta() -> None:
    global _instrumented
    if not AGENTA_ENABLED or _instrumented:
        return
    try:
        ag.init()
        from opentelemetry.instrumentation.langchain import LangchainInstrumentor

        LangchainInstrumentor().instrument()
        _instrumented = True
        logger.info("Agenta tracing initialized")
    except Exception:
        logger.warning("Agenta initialization failed, continuing without tracing")


def fetch_prompt(
    app_slug: str,
    environment: str = "production",
) -> ChatPromptTemplate | None:
    if not AGENTA_ENABLED:
        return None
    try:
        config = ag.ConfigManager.get_from_registry(
            app_slug=app_slug,
            environment_slug=environment,
        )
        messages = config["prompt"]["messages"]
        tuples = [(m["role"], m["content"]) for m in messages]
        return ChatPromptTemplate.from_messages(tuples, template_format="jinja2")
    except Exception:
        logger.debug("Failed to fetch prompt '%s' from Agenta, using local fallback", app_slug)
        return None


PROMPT_SLUGS = {
    "summarize-map": "summarize-map",
    "summarize-collapse": "summarize-collapse",
    "summarize-reduce": "summarize-reduce",
    "refine-initial": "refine-initial",
    "refine": "refine",
    "memory": "memory",
    "consistency": "consistency",
    "character-design": "character-design",
}


def fetch_prompts(
    keys: list[str], environment: str = "production"
) -> dict[str, ChatPromptTemplate]:
    result = {}
    for key in keys:
        slug = PROMPT_SLUGS.get(key)
        if not slug:
            continue
        prompt = fetch_prompt(slug, environment=environment)
        if prompt is not None:
            result[key] = prompt
    return result
