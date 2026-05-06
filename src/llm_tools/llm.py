from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.rate_limiters import InMemoryRateLimiter

from llm_tools.config import (
    DEFAULT_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    RATE_LIMIT_CHECK_INTERVAL,
    RATE_LIMIT_MAX_BUCKET,
    RATE_LIMIT_RPS,
    RETRY_MAX_ATTEMPTS,
)


def create_llm(
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0,
    with_retry: bool = True,
) -> BaseChatModel:
    model = model or DEFAULT_MODEL
    api_key = api_key or OPENROUTER_API_KEY
    base_url = base_url or OPENROUTER_BASE_URL

    rate_limiter = InMemoryRateLimiter(
        requests_per_second=RATE_LIMIT_RPS,
        check_every_n_seconds=RATE_LIMIT_CHECK_INTERVAL,
        max_bucket_size=RATE_LIMIT_MAX_BUCKET,
    )

    llm = init_chat_model(
        model=model,
        model_provider="openai",
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        rate_limiter=rate_limiter,
    )

    if with_retry:
        llm = llm.with_retry(
            stop_after_attempt=RETRY_MAX_ATTEMPTS,
            wait_exponential_jitter=True,
            exponential_jitter_params={"initial": 2},
        )

    return llm
