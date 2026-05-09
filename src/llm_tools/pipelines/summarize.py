from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from llm_tools.config import CHUNK_TURNS_DEFAULT, MAX_DIRECT_REDUCE_CHUNKS
from llm_tools.llm import create_llm
from llm_tools.models import ChatSession, MemoryChunk, SessionMemory
from llm_tools.prompts.summarize import COLLAPSE_PROMPT, MAP_PROMPT, REDUCE_PROMPT


def _group_turns(session: ChatSession, turns_per_chunk: int = CHUNK_TURNS_DEFAULT) -> list[list]:
    return _group_items(session.turns, turns_per_chunk)


def _turns_to_docs(groups: list[list]) -> list[Document]:
    docs = []
    for idx, group in enumerate(groups, start=1):
        character_text = "\n\n".join(t.response for t in group).strip()
        prompt_context = "\n\n".join(
            f"[Turn {t.turn_id} Prompt]\n{t.prompt}" for t in group if t.prompt
        ).strip()

        docs.append(
            Document(
                page_content=character_text,
                metadata={
                    "chunk_id": idx,
                    "turn_ids": [t.turn_id for t in group],
                    "prompt_context": prompt_context,
                },
            )
        )
    return docs


def _group_items(items: list, group_size: int = 8) -> list[list]:
    return [items[i : i + group_size] for i in range(0, len(items), group_size)]


def summarize_session(
    session: ChatSession,
    model: str | None = None,
    turns_per_chunk: int = CHUNK_TURNS_DEFAULT,
    max_concurrency: int = 3,
    prompts: dict[str, ChatPromptTemplate] | None = None,
) -> SessionMemory:
    p = prompts or {}
    _map = p.get("summarize-map") or MAP_PROMPT
    _collapse = p.get("summarize-collapse") or COLLAPSE_PROMPT
    _reduce = p.get("summarize-reduce") or REDUCE_PROMPT

    llm = create_llm(model=model)
    parser = StrOutputParser()

    map_chain = _map | llm | parser
    reduce_chain = _reduce | llm | parser
    collapse_chain = _collapse | llm | parser

    groups = _group_turns(session, turns_per_chunk)
    docs = _turns_to_docs(groups)

    map_inputs = [
        {
            "prompt_context": d.metadata.get("prompt_context", ""),
            "character_text": d.page_content,
        }
        for d in docs
    ]

    map_outputs = map_chain.batch(
        map_inputs,
        config={"max_concurrency": max_concurrency},
    )

    mapped_summaries = [
        MemoryChunk(
            chunk_id=doc.metadata["chunk_id"],
            turn_ids=doc.metadata["turn_ids"],
            summary=summary,
            prompt_context=doc.metadata.get("prompt_context", ""),
        )
        for doc, summary in zip(docs, map_outputs, strict=True)
    ]

    if len(mapped_summaries) > MAX_DIRECT_REDUCE_CHUNKS:
        grouped = _group_items(mapped_summaries, group_size=8)

        collapse_inputs = [
            {
                "chunk_summaries": "\n\n---\n\n".join(
                    f"[Chunk {m.chunk_id} | turns {m.turn_ids}]\n{m.summary}"
                    for m in group
                )
            }
            for group in grouped
        ]

        collapsed_outputs = collapse_chain.batch(
            collapse_inputs,
            config={"max_concurrency": 2},
        )

        reduce_input_text = "\n\n---\n\n".join(
            f"[Collapsed group {idx}]\n{summary}"
            for idx, summary in enumerate(collapsed_outputs, start=1)
        )
    else:
        reduce_input_text = "\n\n---\n\n".join(
            f"[Chunk {m.chunk_id} | turns {m.turn_ids}]\n{m.summary}"
            for m in mapped_summaries
        )

    session_summary = reduce_chain.invoke({"chunk_summaries": reduce_input_text})

    return SessionMemory(
        session_summary=session_summary,
        chunks=mapped_summaries,
    )
