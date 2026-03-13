# NANDA Work RAG Knowledge Base

RAG pipeline over the 8 NANDA Work repos: chunk READMEs, docs, schemas, and optional source; embed with OpenAI; store in Chroma; query with natural language.

## Setup

From NANDA Work root. Use the project venv (Python 3.13) so Chroma works:

  cd "NANDA Work"
  python3.13 -m venv knowledge-base/.venv
  source knowledge-base/.venv/bin/activate   # or on Windows: knowledge-base\.venv\Scripts\activate
  pip install -r knowledge-base/requirements.txt

Put your OpenAI key in `knowledge-base/.env`:

  cp knowledge-base/.env.example knowledge-base/.env
  # Edit knowledge-base/.env and set OPENAI_API_KEY=sk-...

(On macOS with only Python 3.14, use Homebrew Python 3.13: `brew install python@3.13`, then use `python3.13` for the venv.)

## Ingest

With the venv activated:

  python knowledge-base/ingest.py              # docs + schemas
  python knowledge-base/ingest.py --with-code   # include key source
  python knowledge-base/ingest.py --dry-run    # no DB write

## Query

  python knowledge-base/query.py "How does the adapter start the server?"
  python3 knowledge-base/query.py "x402-NP payment flow?" --repo nanda-payments
  python3 knowledge-base/query.py "OAuth setup" --content-type doc --top-k 10

Flags: --repo REPO, --content-type doc|schema|code, --top-k N

## Config

Edit knowledge-base/config.py for REPO_FOLDERS, CHUNK_SIZE, EMBEDDING_MODEL, LLM_MODEL, CHROMA_PERSIST_DIR.
