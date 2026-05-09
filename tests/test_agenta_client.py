from unittest.mock import MagicMock, patch

from langchain_core.prompts import ChatPromptTemplate


def _patch_config(return_value=None, side_effect=None):
    kwargs = {}
    if return_value is not None:
        kwargs["return_value"] = return_value
    if side_effect is not None:
        kwargs["side_effect"] = side_effect
    return patch(
        "llm_tools.agenta_client.ag.ConfigManager.get_from_registry",
        **kwargs,
    )


def test_fetch_prompt_returns_chat_prompt_template():
    config = {
        "prompt": {
            "messages": [
                {"role": "system", "content": "You are a summarizer."},
                {"role": "user", "content": "Summarize: {{text}}"},
            ],
        },
    }

    with patch("llm_tools.agenta_client.AGENTA_ENABLED", True), \
         _patch_config(return_value=config):
        from llm_tools.agenta_client import fetch_prompt

        result = fetch_prompt("summarize-map")

    assert isinstance(result, ChatPromptTemplate)
    messages = result.messages
    assert len(messages) == 2


def test_fetch_prompt_returns_none_when_disabled():
    with patch("llm_tools.agenta_client.AGENTA_ENABLED", False):
        from llm_tools.agenta_client import fetch_prompt

        result = fetch_prompt("summarize-map")

    assert result is None


def test_fetch_prompt_returns_none_on_error():
    with patch("llm_tools.agenta_client.AGENTA_ENABLED", True), \
         _patch_config(side_effect=Exception("connection error")):
        from llm_tools.agenta_client import fetch_prompt

        result = fetch_prompt("summarize-map")

    assert result is None


def test_init_agenta_skips_when_disabled():
    with patch("llm_tools.agenta_client.AGENTA_ENABLED", False):
        from llm_tools.agenta_client import _instrumented, init_agenta

        init_agenta()
        assert not _instrumented


def test_init_agenta_instruments_on_success():
    mock_instrumentor = MagicMock()
    instr_path = (
        "opentelemetry.instrumentation.langchain"
        ".LangchainInstrumentor"
    )

    with patch("llm_tools.agenta_client.AGENTA_ENABLED", True), \
         patch("llm_tools.agenta_client.ag") as mock_ag, \
         patch(instr_path, return_value=mock_instrumentor):
        import llm_tools.agenta_client as mod

        mod._instrumented = False
        mod.init_agenta()

        mock_ag.init.assert_called_once()
        mock_instrumentor.instrument.assert_called_once()
        assert mod._instrumented is True


def test_init_agenta_fails_gracefully():
    with patch("llm_tools.agenta_client.AGENTA_ENABLED", True), \
         patch("llm_tools.agenta_client.ag") as mock_ag:
        mock_ag.init.side_effect = Exception("init failed")

        import llm_tools.agenta_client as mod

        mod._instrumented = False
        mod.init_agenta()

        assert not mod._instrumented


def test_fetch_prompts_batch():
    config = {
        "prompt": {
            "messages": [
                {"role": "system", "content": "Test"},
                {"role": "user", "content": "{{input}}"},
            ],
        },
    }

    with patch("llm_tools.agenta_client.AGENTA_ENABLED", True), \
         _patch_config(return_value=config):
        from llm_tools.agenta_client import fetch_prompts

        result = fetch_prompts(["summarize-map", "summarize-reduce"])

    assert "summarize-map" in result
    assert "summarize-reduce" in result
    assert isinstance(result["summarize-map"], ChatPromptTemplate)


def test_fetch_prompts_skips_on_failure():
    def side_effect(**kwargs):
        if kwargs["app_slug"] == "summarize-map":
            return {
                "prompt": {
                    "messages": [{"role": "system", "content": "OK"}],
                },
            }
        raise Exception("not found")

    with patch("llm_tools.agenta_client.AGENTA_ENABLED", True), \
         _patch_config(side_effect=side_effect):
        from llm_tools.agenta_client import fetch_prompts

        result = fetch_prompts(["summarize-map", "summarize-reduce"])

    assert "summarize-map" in result
    assert "summarize-reduce" not in result
