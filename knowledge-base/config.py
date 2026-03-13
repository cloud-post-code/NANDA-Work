"""Configuration for the NANDA Work RAG knowledge base."""
import os
from pathlib import Path

# Repo root = Nanda Docs (where the 8 project folders live in this workspace)
_THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = _THIS_DIR.parent / "Nanda Docs"

# The 8 repo folders to index (under REPO_ROOT)
REPO_FOLDERS = [
    "chat-frontend",
    "adapter",
    "nanda-payments",
    "mcp-index",
    "nanda-agent",
    "agentfacts-format",
    "list-39",
    "nanda-index-frontend",
]

# Paths/patterns to exclude from indexing
EXCLUDE_DIRS = {"node_modules", "__pycache__", ".git", "dist", "build", ".venv", "venv"}
EXCLUDE_FILES = {"package-lock.json", "*.min.js"}

# Include patterns per content type: (glob, content_type)
# Markdown: all .md
# Schemas: schemas/*.json, *schema*.json
DOC_GLOBS = ["**/*.md"]
SCHEMA_GLOBS = ["**/schemas/*.json", "**/*schema*.json"]
# Code (phase 2): key source only
CODE_GLOBS = [
    "**/*.py",
    "**/src/**/*.ts",
    "**/src/**/*.js",
    "**/nanda_adapter/**/*.py",
]

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Embedding
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Vector DB
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(_THIS_DIR / "chroma_db"))
COLLECTION_NAME = "nanda_work"

# Query
TOP_K = 8
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
