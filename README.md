# NANDA Work

This workspace contains **two main areas**: a RAG **knowledge-base** over NANDA ecosystem docs, and **Nanda Docs** (the reference copies of the cloud-post-code projects). The root repo tracks the workspace; the 8 project folders live under Nanda Docs and are not separate git repos here.

---

## knowledge-base

**Purpose:** RAG (retrieval-augmented generation) pipeline over the NANDA ecosystem. It chunks READMEs, docs, schemas, and optional source from the 8 projects, embeds with OpenAI, stores in Chroma, and answers natural-language questions.

**What’s inside:**

| Path | Role |
|------|------|
| `config.py` | Repo root, folder list to index, chunk/embed/Chroma settings, env overrides. |
| `ingest.py` | Scans repo folders → chunks by type (doc/schema/code) → embeds → upserts into Chroma. |
| `query.py` | Embeds the question, retrieves top-k chunks, calls LLM, returns answer. |
| `requirements.txt` | Python deps (LangChain, OpenAI, Chroma, etc.). |
| `.env` | `OPENAI_API_KEY` (and optional `OPENAI_EMBEDDING_MODEL`, `OPENAI_LLM_MODEL`, `CHROMA_PERSIST_DIR`). |
| `chroma_db/` | Persisted Chroma vector DB (gitignored). |
| `.venv/` | Python virtualenv (gitignored). |

**Run from NANDA Work root:**

- **Ingest:**  
  `python knowledge-base/ingest.py`  
  Optional: `--with-code` (include key source), `--dry-run` (no DB write).
- **Query:**  
  `python knowledge-base/query.py "How does the adapter start the server?"`  
  Optional: `--repo REPO`, `--content-type doc|schema|code`, `--top-k N`.

**Indexed content:** `config.py` sets `REPO_ROOT` to **Nanda Docs**, so the 8 project folders there (`chat-frontend`, `adapter`, etc.) are what gets indexed.

---

## Nanda Docs

**Purpose:** Single folder containing the **8 [cloud-post-code](https://github.com/cloud-post-code) project snapshots** (files only, no git). Used as reference documentation and as the source that **knowledge-base** indexes when `REPO_ROOT` points here.

**What’s inside:**

| Folder | Contents |
|--------|----------|
| `chat-frontend` | Chat UI (HTML/JS/CSS), OAuth, `dev` branch snapshot. |
| `adapter` | NANDA adapter (Python): `nanda_adapter` package, examples (LangChain/CrewAI). |
| `nanda-payments` | NANDA Points MCP server (TypeScript/Node): MongoDB, x402-NP, routes, schemas. |
| `mcp-index` | MCP servers API docs (README). |
| `nanda-agent` | Multi-agent runner scripts and bridge (Python/Shell). |
| `agentfacts-format` | AgentFacts schema and README (JSON + docs). |
| `list-39` | List39 agent registry (Node/Express, MongoDB, OAuth). |
| `nanda-index-frontend` | NANDA Index web UI (Node, `master` branch snapshot). |

These are **reference copies** for reading and for RAG; to contribute upstream, use the official repos (e.g. cloud-post-code/chat-frontend) and open PRs there.

---

## How Cursor should understand this workspace

- **knowledge-base** is the **active Python/RAG app**: edit `config.py`, `ingest.py`, and `query.py` here. Use the project’s `.venv` and `requirements.txt`; secrets live in `knowledge-base/.env`. When answering questions about the NANDA ecosystem, prefer using the RAG pipeline (run `query.py`) when you need up-to-date doc/schema/code context; the indexed content is the **Nanda Docs** tree (when `REPO_ROOT` points at it).
- **Nanda Docs** is **reference material**: multiple languages (Python, TypeScript, JavaScript, HTML/CSS, Shell). Treat it as the source of truth for “what the 8 projects contain.” When editing Nanda Docs, you’re changing the local reference copy that knowledge-base indexes; to change upstream projects, work in the official cloud-post-code repos.
- **Workspace root** is the **single git repo** (this README, `.gitignore`, etc.). The 8 project folders under Nanda Docs are not separate repos in this workspace; they are listed in root `.gitignore` only if you keep them out of version control by choice.

---

## Quick reference

| Goal | Where to look / run |
|------|----------------------|
| Ask questions about NANDA docs/schemas/code | Run `knowledge-base/query.py` (after ingest with `REPO_ROOT` → Nanda Docs). |
| Change what gets indexed or how | `knowledge-base/config.py`, `knowledge-base/ingest.py`. |
| Change RAG query behavior or prompts | `knowledge-base/query.py`. |
| Read or copy NANDA project code/docs | `Nanda Docs/<project-name>/`. |
| Push workspace (README, config, knowledge-base code) | Commit and push from NANDA Work root; remote is this repo (e.g. cloud-post-code/NANDA-Work). |
