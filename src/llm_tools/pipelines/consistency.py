from pathlib import Path

from langchain_core.output_parsers import StrOutputParser

from llm_tools.llm import create_llm
from llm_tools.models import ConsistencyReport, ConsistencyViolation
from llm_tools.prompts.consistency import CONSISTENCY_PROMPT


def check_consistency(
    content: str,
    norms: str,
    source: str = "",
    model: str | None = None,
) -> ConsistencyReport:
    llm = create_llm(model=model)
    chain = CONSISTENCY_PROMPT | llm | StrOutputParser()

    output = chain.invoke({"content": content, "norms": norms})

    violations = _parse_violations(output, "Violations")
    warnings = _parse_violations(output, "Warnings")
    observations = _parse_violations(output, "Observations", default_severity="observation")

    all_items = violations + warnings + observations
    summary = _extract_section(output, "Overall assessment")

    return ConsistencyReport(
        source=source,
        violations=all_items,
        summary=summary,
    )


def check_file_consistency(
    content_file: Path | str,
    norms_file: Path | str,
    model: str | None = None,
) -> ConsistencyReport:
    content = Path(content_file).read_text(encoding="utf-8")
    norms = Path(norms_file).read_text(encoding="utf-8")
    return check_consistency(content, norms, source=str(content_file), model=model)


def _extract_section(text: str, header: str) -> str:
    lines = text.split("\n")
    capturing = False
    result: list[str] = []

    for line in lines:
        if line.strip().startswith(f"## {header}"):
            capturing = True
            continue
        if capturing and line.strip().startswith("## "):
            break
        if capturing:
            result.append(line)

    return "\n".join(result).strip()


def _parse_violations(
    text: str, header: str, default_severity: str | None = None
) -> list[ConsistencyViolation]:
    section = _extract_section(text, header)
    if not section:
        return []

    severity = default_severity or header.lower().rstrip("s")
    violations: list[ConsistencyViolation] = []
    current: dict | None = None

    for line in section.split("\n"):
        stripped = line.strip()
        if not stripped:
            if current:
                violations.append(ConsistencyViolation(**current))
                current = None
            continue

        if stripped.startswith("- **Quote") or stripped.startswith("- **quote"):
            if current is None:
                current = {"category": "unknown", "severity": severity, "description": ""}
            quote_text = stripped.split("**:", 1)[-1].strip().strip("*").strip()
            current["quote"] = quote_text
        elif stripped.startswith("- **") and "**:" in stripped:
            if current is not None:
                violations.append(ConsistencyViolation(**current))
            current = {"category": "unknown", "severity": severity, "description": ""}
            label = stripped.split("**", 1)[1].split("**", 1)[0].strip(": ")
            current["category"] = label
            desc = stripped.split("**:", 1)[-1].strip() if "**:" in stripped else stripped
            current["description"] = desc
        elif stripped.startswith("- "):
            if current:
                violations.append(ConsistencyViolation(**current))
            current = {
                "category": "general",
                "severity": severity,
                "description": stripped[2:].strip(),
            }
        elif current and stripped:
            current["description"] += " " + stripped

    if current:
        violations.append(ConsistencyViolation(**current))

    return violations
