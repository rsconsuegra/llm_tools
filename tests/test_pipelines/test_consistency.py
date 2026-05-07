from unittest.mock import MagicMock, patch

from llm_tools.models import ConsistencyReport
from llm_tools.parsers.markdown import extract_section
from llm_tools.pipelines.consistency import (
    _parse_violations,
    check_consistency,
    check_file_consistency,
)

SAMPLE_LLM_OUTPUT = """\
## Violations
- **Tone**: The passage uses modern slang which violates the formal tone rule.
- **Continuity**: Lunessa claims she has never left the village, \
but chapter 2 established she visited Eisenford.

## Warnings
- **Pacing**: The scene introduces three new characters in quick \
succession without development.

## Observations
- The dialogue format changed from italics to plain text mid-scene.

## Overall assessment
The content has two clear violations (tone and continuity) and one pacing concern.
The tone violations are minor and easy to fix. The continuity issue requires
revisiting the chapter 2 reference.
"""


def test_extract_section():
    result = extract_section(SAMPLE_LLM_OUTPUT, "Overall assessment")
    assert "two clear violations" in result


def test_parse_violations():
    violations = _parse_violations(SAMPLE_LLM_OUTPUT, "Violations")
    assert len(violations) == 2
    assert violations[0].severity == "violation"


def test_parse_warnings():
    warnings = _parse_violations(SAMPLE_LLM_OUTPUT, "Warnings")
    assert len(warnings) == 1
    assert warnings[0].severity == "warning"


def test_parse_observations():
    obs = _parse_violations(SAMPLE_LLM_OUTPUT, "Observations", default_severity="observation")
    assert len(obs) == 1
    assert obs[0].severity == "observation"


def test_check_consistency_integration():
    with patch("llm_tools.pipelines.consistency.create_llm") as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm

        with patch("llm_tools.pipelines.consistency.CONSISTENCY_PROMPT") as mock_prompt:
            mock_pipe = MagicMock()
            mock_pipe.__or__ = MagicMock(return_value=MagicMock())
            mock_pipe.__or__.return_value.invoke.return_value = SAMPLE_LLM_OUTPUT
            mock_prompt.__or__ = MagicMock(return_value=mock_pipe)

            report = check_consistency(
                content="Some content to check",
                norms="Rule 1: Use formal tone",
                source="test.md",
            )

    assert isinstance(report, ConsistencyReport)
    assert len(report.violations) == 4
    assert "two clear violations" in report.summary


def test_check_file_consistency(tmp_path):
    content_file = tmp_path / "chapter.md"
    norms_file = tmp_path / "rules.md"
    content_file.write_text("The quick brown fox.")
    norms_file.write_text("Rule 1: No foxes.")

    with patch("llm_tools.pipelines.consistency.check_consistency") as mock_check:
        mock_check.return_value = ConsistencyReport(
            source=str(content_file),
            violations=[],
            summary="Passed.",
        )
        result = check_file_consistency(content_file, norms_file)

    assert result.summary == "Passed."
    assert result.source == str(content_file)
