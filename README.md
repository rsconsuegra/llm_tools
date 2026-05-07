# llm-tools

LLM-powered pipelines for CYOA narrative tooling. Built for a co-written AI visual novel using [OpenWebUI](https://github.com/open-webui/open-webui) and [SillyTavern](https://github.com/SillyTavern/SillyTavern).

## What it does

Automates the workflows around AI-assisted narrative creation:

- **Session summarization** — condense chat logs into structured memory chunks
- **Narrative condensation** — refine long prose (prologues, backstories) into coherent summaries
- **Memory generation** — extract canon facts, character state, and continuation hooks
- **JSONL output** — save structured data for RAG, vector search, and session recall

## Two summarization strategies

### MapReduce — memory extraction and organization

Summarize chunks independently, then combine into one final memory.

```
chunk 1 → summary 1 ─┐
chunk 2 → summary 2 ─┤
chunk 3 → summary 3 ─┼→ final session memory
chunk 4 → summary 4 ─┘
```

- Chunks are processed in parallel via `.batch()` with configurable concurrency
- Each chunk keeps traceable metadata (chunk_id, turn_ids, prompt_context)
- For long sessions (>10 chunks), an automatic **collapse step** compresses intermediate summaries before the final reduce: `Map → Collapse → Reduce`
- Output includes both individual memory chunks and a global session summary

**Best for:** chat session logs, canon extraction, RAG-ready memory chunks, any content where chunks are semi-independent.

### Refine — coherent rewrite of one evolving text

Start with a first summary, then improve it sequentially as each new chunk is processed.

```
chunk 1 → initial summary
initial summary + chunk 2 → revised summary
revised summary + chunk 3 → revised summary
revised summary + chunk 4 → final summary
```

- Sequential by design — each step depends on the previous output
- Optional `--context` flag lets you inject per-run instructions (e.g., "This is a prologue for character X")
- Context is injected only into the initial prompt, not repeated on every refinement step

**Best for:** prologues, character backstories, chapter recaps, timelines, any sequential narrative where flow matters.

### When to use which

| Input | Pipeline | Why |
|---|---|---|
| Chat session logs | MapReduce (`summarize`) | Independent chunks, parallelizable, traceable |
| Prologues, backstories, chapters | Refine (`refine`) | Sequential flow, polished output |
| Canon database / memory chunks | MapReduce | Structured extraction |
| Story bible generation | MapReduce + `--polish` | Extract facts, then polish into prose |

### Hybrid: summarize --polish

The `summarize` command accepts a `--polish` flag that runs the MapReduce pipeline first, then passes the session summary through the Refine pipeline for polished prose output.

## Installation

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```bash
git clone https://github.com/rsconsuegra/llm_tools.git
cd llm_tools
uv sync --extra dev    # includes pytest, ruff
uv sync                # runtime only (no dev tools)
```

## Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_KEY=sk-or-v1-...
```

The project uses [OpenRouter](https://openrouter.ai/) as the LLM gateway. The default model is `nousresearch/hermes-3-llama-3.1-405b:free`.

Short aliases are available via `--model`:

| Alias | Resolves to |
|---|---|
| `hermes-405b` | `nousresearch/hermes-3-llama-3.1-405b:free` |
| `glm-4.5-air` | `z-ai/glm-4.5-air:free` |

You can also pass the full model string directly. Aliases are defined in `src/llm_tools/config.py`.

## CLI Usage

```bash
# Summarize a SillyTavern chat session (MapReduce)
llm-tools summarize chat.jsonl -o memories.jsonl

# Summarize with custom character name and model alias
llm-tools summarize chat.jsonl -c Lunessa -m glm-4.5-air -o memories.jsonl

# Summarize and polish into readable prose
llm-tools summarize chat.jsonl --polish -o memories.jsonl

# Refine a narrative text file
llm-tools refine prologue.md -o summary.jsonl

# Refine with context instructions
llm-tools refine prologue.md --context "Prologue for Lunessa" --chunk-size 3000 -o summary.jsonl

# Print to stdout instead of file
llm-tools summarize chat.jsonl
llm-tools refine prologue.md --context "Character backstory"
```

### Options

**`summarize`**

| Flag | Default | Description |
|---|---|---|
| `--format`, `-f` | `sillytavern` | Chat export format (`sillytavern` \| `openwebui`) |
| `--output`, `-o` | stdout | Output JSONL path |
| `--model`, `-m` | `hermes-405b` | LLM model alias or full model string |
| `--character`, `-c` | `Miah` | Character name in chat |
| `--chunk-size` | `4` | Turns per map chunk |
| `--concurrency` | `3` | Max concurrent LLM calls |
| `--polish` | `false` | Refine session summary into polished prose |

**`refine`**

| Flag | Default | Description |
|---|---|---|
| `--output`, `-o` | stdout | Output JSONL path |
| `--model`, `-m` | `hermes-405b` | LLM model alias or full model string |
| `--chunk-size` | `5000` | Characters per text chunk |
| `--overlap` | `100` | Character overlap between chunks |
| `--context` | none | Additional instructions for summarizer |

## Library Usage

```python
from llm_tools.parsers import SillyTavernParser
from llm_tools.pipelines import summarize_session, refine_file

# MapReduce on a chat session
parser = SillyTavernParser(character_name="Miah")
session = parser.parse("chat.jsonl")
result = summarize_session(session, model="hermes-405b")
print(result.session_summary)

# Refine a narrative text
summary = refine_file("prologue.md", context="Prologue for Lunessa")
print(summary.summary)
```

## Project Structure

```
src/llm_tools/
├── config.py          # Env vars, model registry, defaults
├── llm.py             # LLM factory (alias resolution, rate limiter, retry)
├── models.py          # Pydantic models: Turn, ChatSession, MemoryChunk, TextSummary
├── cli.py             # Typer CLI (summarize + refine commands)
├── parsers/
│   ├── base.py        # Abstract parser protocol
│   ├── silly_tavern.py
│   └── open_webui.py  # Stub
├── pipelines/
│   ├── summarize.py   # MapReduce with optional collapse
│   ├── refine.py      # Sequential refinement
│   ├── memory.py      # Stub
│   └── consistency.py # Stub
├── prompts/
│   ├── summarize.py   # MAP, COLLAPSE, REDUCE prompts
│   ├── refine.py      # REFINE_INITIAL, REFINE prompts
│   ├── memory.py      # Stub
│   └── consistency.py # Stub
└── io_/
    ├── __init__.py    # Re-exports jsonl helpers
    └── jsonl.py       # JSONL read/write for LangChain Documents
notebooks/              # Original prototype notebooks
├── Summarize_MapReduce.ipynb
├── TesPrologue.ipynb
└── Untitled.ipynb
tests/                  # 15 tests
├── conftest.py         # Shared fixtures (sample SillyTavern JSONL)
├── test_llm.py         # Alias resolution tests
├── test_parsers/
│   └── test_silly_tavern.py
└── test_pipelines/
    ├── test_refine.py
    └── test_summarize.py
```

## Development

```bash
make install     # Install all dependencies (including dev)
make test        # Run 15 tests with verbose output
make lint        # Check with ruff
make lint-fix    # Auto-fix lint issues
make run         # Show CLI help
```

## Roadmap

- [ ] OpenWebUI parser
- [ ] Per-character memory pipeline
- [ ] Consistency/norm checking
- [ ] RAG retrieval over JSONL memories
- [ ] Streaming output for refine command
- [ ] Structured JSON output for memory chunks
