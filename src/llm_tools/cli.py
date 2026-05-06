from pathlib import Path

import typer  # noqa: B008  (typer uses function calls as defaults by design)
from langchain_core.documents import Document

from llm_tools.io_.jsonl import save_docs_to_jsonl
from llm_tools.parsers.silly_tavern import SillyTavernParser
from llm_tools.pipelines.summarize import summarize_session

app = typer.Typer(help="LLM-powered pipelines for CYOA narrative tooling")

_chat_file = typer.Argument(..., exists=True, help="Path to chat export file")
_format = typer.Option("sillytavern", "--format", "-f", help="sillytavern | openwebui")
_output = typer.Option(None, "--output", "-o", help="Output JSONL path")
_model = typer.Option(None, "--model", "-m", help="LLM model name or alias")
_character = typer.Option("Miah", "--character", "-c", help="Character name in chat")
_chunk_size = typer.Option(4, "--chunk-size", help="Turns per map chunk")


@app.command()
def summarize(
    chat_file: Path = _chat_file,
    format: str = _format,
    output: Path | None = _output,
    model: str | None = _model,
    character: str = _character,
    turns_per_chunk: int = _chunk_size,
):
    parser = _get_parser(format, character)
    session = parser.parse(chat_file)
    typer.echo(f"Parsed {len(session.turns)} turns from {chat_file}")

    result = summarize_session(session, model=model, turns_per_chunk=turns_per_chunk)

    typer.echo(f"Generated {len(result.chunks)} memory chunks + session summary")

    if output:
        docs = [
            Document(
                page_content=chunk.summary,
                metadata={
                    "type": "memory_chunk",
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
                metadata={"type": "session_memory"},
            )
        )
        save_docs_to_jsonl(docs, str(output))
        typer.echo(f"Saved to {output}")
    else:
        typer.echo("\n--- Session Summary ---\n")
        typer.echo(result.session_summary)


def _get_parser(format: str, character: str):
    if format == "sillytavern":
        return SillyTavernParser(character_name=character)
    raise ValueError(f"Unknown format: {format}. Supported: sillytavern")
