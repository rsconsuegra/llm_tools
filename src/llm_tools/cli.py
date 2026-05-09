from pathlib import Path

import typer  # noqa: B008  (typer uses function calls as defaults by design)
from langchain_core.documents import Document

from llm_tools.agenta_client import fetch_prompts, init_agenta
from llm_tools.config import AGENTA_ENABLED, DEFAULT_MODEL
from llm_tools.io_.jsonl import save_docs_to_jsonl
from llm_tools.parsers.silly_tavern import SillyTavernParser
from llm_tools.pipelines.character_design import generate_character
from llm_tools.pipelines.consistency import check_file_consistency
from llm_tools.pipelines.memory import extract_character_state
from llm_tools.pipelines.refine import refine_file, refine_text
from llm_tools.pipelines.summarize import summarize_session

app = typer.Typer(help="LLM-powered pipelines for CYOA narrative tooling")
generate_app = typer.Typer(help="Generate structured narrative content")
app.add_typer(generate_app, name="generate")

_chat_file = typer.Argument(..., exists=True, help="Path to chat export file")
_text_file = typer.Argument(..., exists=True, help="Path to text/markdown file")
_format = typer.Option("sillytavern", "--format", "-f", help="sillytavern | openwebui")
_output = typer.Option(None, "--output", "-o", help="Output JSONL path")
_model = typer.Option(None, "--model", "-m", help="LLM model name or alias")
_character = typer.Option("Miah", "--character", "-c", help="Character name in chat")
_chunk_size = typer.Option(4, "--chunk-size", help="Turns per map chunk")
_concurrency = typer.Option(3, "--concurrency", help="Max concurrent LLM calls for map step")
_chunk_chars = typer.Option(5000, "--chunk-size", help="Characters per text chunk")
_overlap = typer.Option(100, "--overlap", help="Character overlap between chunks")
_context = typer.Option(None, "--context", help="Additional instructions for summarizer")
_polish = typer.Option(False, "--polish", help="Refine session summary into polished prose")
_norms = typer.Option(..., exists=True, help="Path to norms/rules document")


@app.callback()
def _main():
    init_agenta()


def _resolve_model_name(model: str | None) -> str:
    return model or DEFAULT_MODEL


def _output_results(docs: list[Document], output: Path | None, model_name: str) -> None:
    if output:
        save_docs_to_jsonl(docs, str(output))
        typer.echo(f"Saved to {output}")
    else:
        for doc in docs:
            typer.echo(doc.page_content)


@app.command()
def summarize(
    chat_file: Path = _chat_file,
    format: str = _format,
    output: Path | None = _output,
    model: str | None = _model,
    character: str = _character,
    turns_per_chunk: int = _chunk_size,
    max_concurrency: int = _concurrency,
    polish: bool = _polish,
):
    if AGENTA_ENABLED:
        prompts = fetch_prompts(
            ["summarize-map", "summarize-collapse", "summarize-reduce"]
        )
    else:
        prompts = {}

    parser = _get_parser(format, character)
    session = parser.parse(chat_file)
    typer.echo(f"Parsed {len(session.turns)} turns from {chat_file}")

    result = summarize_session(
        session,
        model=model,
        turns_per_chunk=turns_per_chunk,
        max_concurrency=max_concurrency,
        prompts=prompts,
    )

    if polish:
        polish_prompts = fetch_prompts(["refine-initial", "refine"]) if AGENTA_ENABLED else {}
        polished = refine_text(
            result.session_summary,
            source=str(chat_file),
            model=model,
            context="Polish this session memory into coherent, readable prose",
            prompts=polish_prompts,
        )
        result.session_summary = polished.summary
        typer.echo(f"Generated {len(result.chunks)} chunks + polished session summary")
    else:
        typer.echo(f"Generated {len(result.chunks)} memory chunks + session summary")

    model_name = _resolve_model_name(model)
    docs = [
        Document(
            page_content=chunk.summary,
            metadata={
                "type": "memory_chunk",
                "model": model_name,
                "chunk_id": chunk.chunk_id,
                "turn_ids": chunk.turn_ids,
                "prompt_context": chunk.prompt_context,
            },
        )
        for chunk in result.chunks
    ]
    docs.append(
        Document(
            page_content=result.session_summary,
            metadata={
                "type": "session_memory",
                "model": model_name,
                "source_chunks": len(result.chunks),
            },
        )
    )
    _output_results(docs, output, model_name)


@app.command()
def refine(
    text_file: Path = _text_file,
    output: Path | None = _output,
    model: str | None = _model,
    chunk_size: int = _chunk_chars,
    overlap: int = _overlap,
    context: str | None = _context,
):
    prompts = fetch_prompts(["refine-initial", "refine"]) if AGENTA_ENABLED else {}

    result = refine_file(
        text_file,
        model=model,
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        context=context,
        prompts=prompts,
    )
    typer.echo(f"Refined {result.n_chunks} chunks from {text_file}")

    model_name = _resolve_model_name(model)
    docs = [
        Document(
            page_content=result.summary,
            metadata={
                "type": "refined_summary",
                "model": model_name,
                "source": result.source,
                "n_chunks": result.n_chunks,
                "chunk_size": result.chunk_size,
                "chunk_overlap": result.chunk_overlap,
                "context": result.context,
            },
        )
    ]
    _output_results(docs, output, model_name)


@app.command()
def memory(
    chat_file: Path = _chat_file,
    character: str = _character,
    format: str = _format,
    output: Path | None = _output,
    model: str | None = _model,
):
    prompts = fetch_prompts(["memory"]) if AGENTA_ENABLED else {}

    parser = _get_parser(format, character)
    session = parser.parse(chat_file)
    typer.echo(f"Parsed {len(session.turns)} turns from {chat_file}")

    state = extract_character_state(session, character_name=character, model=model, prompts=prompts)
    typer.echo(f"Extracted state for {state.name}")

    model_name = _resolve_model_name(model)
    doc = Document(
        page_content=state.model_dump_json(indent=2),
        metadata={
            "type": "character_state",
            "model": model_name,
            "character": state.name,
            "source": str(chat_file),
            "source_turns": state.source_turns,
        },
    )
    _output_results([doc], output, model_name)


@app.command()
def check(
    text_file: Path = _text_file,
    norms: Path = _norms,
    output: Path | None = _output,
    model: str | None = _model,
):
    prompts = fetch_prompts(["consistency"]) if AGENTA_ENABLED else {}

    report = check_file_consistency(text_file, norms, model=model, prompts=prompts)

    n_violations = sum(1 for v in report.violations if v.severity == "violation")
    n_warnings = sum(1 for v in report.violations if v.severity == "warning")
    n_obs = sum(1 for v in report.violations if v.severity == "observation")
    typer.echo(f"Found {n_violations} violations, {n_warnings} warnings, {n_obs} observations")

    model_name = _resolve_model_name(model)
    docs = [
        Document(
            page_content=v.model_dump_json(indent=2),
            metadata={
                "type": "consistency_finding",
                "model": model_name,
                "severity": v.severity,
                "category": v.category,
                "source": report.source,
            },
        )
        for v in report.violations
    ]
    docs.append(
        Document(
            page_content=report.summary,
            metadata={
                "type": "consistency_summary",
                "model": model_name,
                "source": report.source,
            },
        )
    )
    _output_results(docs, output, model_name)


@generate_app.command("character")
def generate_character_cmd(
    concept: str = typer.Argument(..., help="Rough character concept description"),
    output: Path | None = _output,
    model: str | None = _model,
):
    prompts = fetch_prompts(["character-design"]) if AGENTA_ENABLED else {}

    design = generate_character(concept, model=model, prompts=prompts)
    typer.echo(f"Generated character: {design.name} ({design.role})")

    model_name = _resolve_model_name(model)
    doc = Document(
        page_content=design.model_dump_json(indent=2),
        metadata={
            "type": "character_design",
            "model": model_name,
            "character": design.name,
        },
    )
    _output_results([doc], output, model_name)


def _get_parser(format: str, character: str):
    if format == "sillytavern":
        return SillyTavernParser(character_name=character)
    raise ValueError(f"Unknown format: {format}. Supported: sillytavern")
