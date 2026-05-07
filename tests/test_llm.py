from llm_tools.config import MODELS
from llm_tools.llm import _resolve_model


def test_alias_resolves():
    assert _resolve_model("hermes-405b") == MODELS["hermes-405b"]
    assert _resolve_model("glm-4.5-air") == MODELS["glm-4.5-air"]


def test_full_model_name_passes_through():
    full = "nousresearch/hermes-3-llama-3.1-405b:free"
    assert _resolve_model(full) == full


def test_unknown_string_passes_through():
    assert _resolve_model("some-unknown-model") == "some-unknown-model"
