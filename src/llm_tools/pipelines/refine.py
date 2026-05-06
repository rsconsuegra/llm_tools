from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from llm_tools.llm import create_llm
from llm_tools.models import TextSummary
from llm_tools.prompts.refine import REFINE_INITIAL_PROMPT, REFINE_PROMPT


def refine_text(
    text: str,
    source: str = "",
    model: str | None = None,
    chunk_size: int = 5000,
    chunk_overlap: int = 100,
    context: str | None = None,
) -> TextSummary:
    llm = create_llm(model=model)
    parser = StrOutputParser()

    initial_chain = REFINE_INITIAL_PROMPT | llm | parser
    refine_chain = REFINE_PROMPT | llm | parser

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_text(text)

    context_block = f"CONTEXT: {context}\n\n" if context else ""

    summary = initial_chain.invoke({"text": chunks[0], "context_block": context_block})

    for chunk in chunks[1:]:
        summary = refine_chain.invoke({"existing_summary": summary, "text": chunk})

    return TextSummary(
        source=source,
        summary=summary,
        n_chunks=len(chunks),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        context=context,
    )


def refine_file(
    file_path: Path | str,
    model: str | None = None,
    chunk_size: int = 5000,
    chunk_overlap: int = 100,
    context: str | None = None,
) -> TextSummary:
    text = Path(file_path).read_text(encoding="utf-8")
    return refine_text(
        text,
        source=str(file_path),
        model=model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        context=context,
    )
