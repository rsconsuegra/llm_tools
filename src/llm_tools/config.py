from os import getenv

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = getenv("OPENROUTER_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DEFAULT_MODEL = "nousresearch/hermes-3-llama-3.1-405b:free"

MODELS = {
    "hermes-405b": "nousresearch/hermes-3-llama-3.1-405b:free",
    "glm-4.5-air": "z-ai/glm-4.5-air:free",
}

RATE_LIMIT_RPS = 0.1
RATE_LIMIT_CHECK_INTERVAL = 0.1
RATE_LIMIT_MAX_BUCKET = 10

RETRY_MAX_ATTEMPTS = 3

CHUNK_TURNS_DEFAULT = 4
