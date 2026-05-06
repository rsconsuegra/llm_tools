from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from llm_tools.config import CHUNK_TURNS_DEFAULT
from llm_tools.llm import create_llm
from llm_tools.models import ChatSession, MemoryChunk, SessionMemory
from llm_tools.prompts.summarize import MAP_PROMPT, REDUCE_PROMPT


def _group_turns(session: ChatSession, turns_per_chunk: int = CHUNK_TURNS_DEFAULT) -> list[list]:
    chunks = []
    for i in range(0, len(session.turns), turns_per_chunk):
        chunks.append(session.turns[i : i + turns_per_chunk])
    return chunks


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


def summarize_session(
    session: ChatSession,
    model: str | None = None,
    turns_per_chunk: int = CHUNK_TURNS_DEFAULT,
) -> SessionMemory:
    llm = create_llm(model=model)
    parser = StrOutputParser()

    map_chain = MAP_PROMPT | llm | parser
    reduce_chain = REDUCE_PROMPT | llm | parser

    groups = _group_turns(session, turns_per_chunk)
    docs = _turns_to_docs(groups)

    mapped_summaries: list[MemoryChunk] = []
    for d in docs:
        summary = map_chain.invoke(
            {
                "prompt_context": d.metadata.get("prompt_context", ""),
                "character_text": d.page_content,
            }
        )
        mapped_summaries.append(
            MemoryChunk(
                chunk_id=d.metadata["chunk_id"],
                turn_ids=d.metadata["turn_ids"],
                summary=summary,
                prompt_context=d.metadata.get("prompt_context", ""),
            )
        )

    chunk_summaries_text = "\n\n---\n\n".join(
        f"[Chunk {m.chunk_id} | turns {m.turn_ids}]\n{m.summary}" for m in mapped_summaries
    )

    session_summary = reduce_chain.invoke({"chunk_summaries": chunk_summaries_text})

    return SessionMemory(
        session_summary=session_summary,
        chunks=mapped_summaries,
    )
