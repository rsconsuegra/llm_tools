from unittest.mock import MagicMock, patch

import pytest

from llm_tools.models import TextSummary
from llm_tools.pipelines.refine import refine_file, refine_text


@pytest.fixture
def long_text():
    return "Word " * 3000


@pytest.fixture
def short_text():
    return "This is a short narrative about a girl named Lunessa who lives in a village."


def test_split_single_chunk(short_text):
    with patch("llm_tools.pipelines.refine.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_llm.__or__ = lambda self, other: other
        mock_create.return_value = mock_llm

        with patch("llm_tools.pipelines.refine.REFINE_INITIAL_PROMPT") as mock_prompt:
            mock_pipe = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_pipe)
            mock_pipe.__or__ = MagicMock(return_value=MagicMock())
            mock_pipe.__or__.return_value.invoke.return_value = "Summary of Lunessa's story."

            result = refine_text(short_text, source="test.md", chunk_size=5000)

    assert isinstance(result, TextSummary)
    assert result.n_chunks == 1
    assert result.source == "test.md"


def test_split_multiple_chunks(long_text):
    with patch("llm_tools.pipelines.refine.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm

        call_count = {"n": 0}

        def fake_invoke(inputs):
            call_count["n"] += 1
            if "existing_summary" not in inputs:
                return "Initial summary."
            return inputs["existing_summary"] + " Refined."

        initial_pipe = MagicMock()
        initial_pipe.invoke = fake_invoke

        with patch("llm_tools.pipelines.refine.REFINE_INITIAL_PROMPT") as mock_init_prompt:
            with patch("llm_tools.pipelines.refine.REFINE_PROMPT") as mock_refine_prompt:
                mock_init_pipe = MagicMock()
                mock_init_pipe.__or__ = MagicMock(return_value=initial_pipe)
                mock_init_prompt.__or__ = MagicMock(return_value=mock_init_pipe)

                mock_refine_pipe = MagicMock()
                mock_refine_pipe.__or__ = MagicMock(return_value=initial_pipe)
                mock_refine_prompt.__or__ = MagicMock(return_value=mock_refine_pipe)

                result = refine_text(
                    long_text, source="long.md",
                    chunk_size=2000, chunk_overlap=200,
                )

    assert result.n_chunks > 1
    assert call_count["n"] == result.n_chunks


def test_context_in_initial_only():
    captured_inputs = []

    def capture_invoke(inputs):
        captured_inputs.append(inputs)
        return "Summary."

    with patch("llm_tools.pipelines.refine.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm

        text = "A " * 6000

        with patch("llm_tools.pipelines.refine.REFINE_INITIAL_PROMPT") as mock_init:
            with patch("llm_tools.pipelines.refine.REFINE_PROMPT") as mock_ref:
                mock_pipe = MagicMock()
                mock_pipe.invoke = capture_invoke
                mock_pipe.__or__ = MagicMock(return_value=mock_pipe)

                mock_init.__or__ = MagicMock(return_value=mock_pipe)
                mock_ref.__or__ = MagicMock(return_value=mock_pipe)

                refine_text(
                    text, context="This is Lunessa's prologue",
                    chunk_size=2000,
                )

    initial_call = captured_inputs[0]
    assert "Lunessa's prologue" in initial_call["context_block"]

    for later_call in captured_inputs[1:]:
        assert "Lunessa" not in later_call.get("context_block", "")


def test_refine_file_reads_utf8(tmp_path):
    file_path = tmp_path / "prologue.md"
    file_path.write_text("Lunessa stood by the creek.", encoding="utf-8")

    with patch("llm_tools.pipelines.refine.refine_text") as mock_refine:
        mock_refine.return_value = TextSummary(
            source=str(file_path), summary="Test", n_chunks=1,
            chunk_size=5000, chunk_overlap=100,
        )
        refine_file(file_path)

    mock_refine.assert_called_once()
    call_kwargs = mock_refine.call_args
    assert call_kwargs.kwargs.get("source") == str(file_path)
