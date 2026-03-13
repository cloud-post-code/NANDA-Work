"""
Ingest pipeline: load docs/schemas (and optionally code) from the 8 repos,
chunk, embed, and upsert into Chroma.
Run from NANDA Work root: python knowledge-base/ingest.py [--dry-run] [--with-code]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

# Load .env from knowledge-base/, repo root, then cwd
try:
    from dotenv import load_dotenv
    _kb_dir = Path(__file__).resolve().parent
    load_dotenv(_kb_dir / ".env")
    load_dotenv(_kb_dir.parent / ".env")  # NANDA Work root
    load_dotenv()
except ImportError:
    pass

from config import (
    REPO_ROOT,
    REPO_FOLDERS,
    EXCLUDE_DIRS,
    DOC_GLOBS,
    SCHEMA_GLOBS,
    CODE_GLOBS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def should_exclude(path: Path) -> bool:
    """Return True if path should be excluded."""
    parts = path.parts
    for d in EXCLUDE_DIRS:
        if d in parts:
            return True
    if path.name == "package-lock.json":
        return True
    if path.suffix == ".json" and "package" in path.name.lower() and path.name != "package.json":
        return False  # allow package.json for context
    return False


def collect_files(repo_path: Path, globs: list[str], content_type: str) -> list[tuple[Path, str]]:
    """Yield (path, content_type) for files matching globs under repo_path."""
    out = []
    for pattern in globs:
        for path in repo_path.glob(pattern):
            if not path.is_file():
                continue
            if should_exclude(path):
                continue
            try:
                path.relative_to(repo_path)
            except ValueError:
                continue
            out.append((path, content_type))
    return out


def read_text(path: Path) -> str:
    """Read file as UTF-8; replace bad chars."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[Error reading {path}: {e}]"


def _get_text_splitter():
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        return RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        return RecursiveCharacterTextSplitter


def chunk_markdown(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split markdown by sections (##) first, then by size."""
    RecursiveCharacterTextSplitter = _get_text_splitter()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


def chunk_json(text: str) -> list[str]:
    """One chunk per file for small JSON; split by top-level keys if large."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [text]
    if isinstance(data, dict):
        items = list(data.items())
        if len(items) <= 4:
            return [text]
        chunks = []
        for k, v in items:
            chunks.append(json.dumps({k: v}, indent=2))
        return chunks
    return [text]


def chunk_code(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Chunk code by size with overlap."""
    RecursiveCharacterTextSplitter = _get_text_splitter()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n\n", "\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


def load_and_chunk(
    include_code: bool = False,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, dict]]:
    """Load all included files from the 8 repos and return list of (text, metadata)."""
    RecursiveCharacterTextSplitter = _get_text_splitter()
    doc_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )

    chunks_with_meta: list[tuple[str, dict]] = []

    for repo_name in REPO_FOLDERS:
        repo_path = REPO_ROOT / repo_name
        if not repo_path.is_dir():
            continue

        # Docs
        for path, _ in collect_files(repo_path, DOC_GLOBS, "doc"):
            text = read_text(path)
            if not text.strip():
                continue
            rel = path.relative_to(repo_path)
            for i, chunk_text in enumerate(doc_splitter.split_text(text)):
                meta = {
                    "repo": repo_name,
                    "file_path": str(rel),
                    "content_type": "doc",
                }
                chunks_with_meta.append((chunk_text, meta))

        # Schemas
        for path, _ in collect_files(repo_path, SCHEMA_GLOBS, "schema"):
            text = read_text(path)
            if not text.strip():
                continue
            rel = path.relative_to(repo_path)
            for chunk_text in chunk_json(text):
                meta = {
                    "repo": repo_name,
                    "file_path": str(rel),
                    "content_type": "schema",
                }
                chunks_with_meta.append((chunk_text, meta))

        # Code (optional)
        if include_code:
            for path, _ in collect_files(repo_path, CODE_GLOBS, "code"):
                if path.suffix == ".json":
                    continue
                text = read_text(path)
                if not text.strip() or len(text) > 100_000:
                    continue
                rel = path.relative_to(repo_path)
                lang = "py" if path.suffix == ".py" else "ts" if path.suffix == ".ts" else "js"
                code_chunks = chunk_code(text, chunk_size, overlap)
                for i, chunk_text in enumerate(code_chunks):
                    meta = {
                        "repo": repo_name,
                        "file_path": str(rel),
                        "content_type": "code",
                        "language": lang,
                    }
                    # Prepend source label so model knows where it's from
                    labeled = f"[{repo_name}/{rel}]\n\n{chunk_text}"
                    chunks_with_meta.append((labeled, meta))

    return chunks_with_meta


def chunk_id(repo: str, file_path: str, index: int) -> str:
    """Stable id for upsert/replace."""
    return hashlib.sha256(f"{repo}:{file_path}:{index}".encode()).hexdigest()[:32]


def run_ingest(dry_run: bool = False, with_code: bool = False) -> None:
    """Load, chunk, embed, and upsert to Chroma."""
    chunks_with_meta = load_and_chunk(include_code=with_code)
    print(f"Total chunks: {len(chunks_with_meta)}")
    if not chunks_with_meta:
        print("No chunks produced. Check REPO_ROOT and REPO_FOLDERS in config.py.")
        return

    if dry_run:
        for i, (text, meta) in enumerate(chunks_with_meta[:5]):
            print(f"--- Chunk {i} ({meta}) ---")
            print(text[:300] + "..." if len(text) > 300 else text)
        print("... (dry run, not writing to DB)")
        return

    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
    except ImportError as e:
        print("Install deps: pip install -r knowledge-base/requirements.txt", file=sys.stderr)
        raise SystemExit(1) from e

    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env or environment.", file=sys.stderr)
        sys.exit(1)

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    persist_dir = Path(CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
    )

    # Build documents and ids for add
    ids = []
    texts = []
    metadatas = []
    for i, (text, meta) in enumerate(chunks_with_meta):
        ids.append(chunk_id(meta["repo"], meta["file_path"], i))
        texts.append(text)
        metadatas.append(meta)

    # Chroma add in batches
    batch_size = 200
    for start in range(0, len(texts), batch_size):
        end = min(start + batch_size, len(texts))
        vectorstore.add_texts(
            texts=texts[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )
        print(f"Upserted {end}/{len(texts)} chunks.")

    print("Ingest complete. Vector store at", persist_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest NANDA Work repos into vector DB")
    parser.add_argument("--dry-run", action="store_true", help="Only load and chunk; print sample, no DB")
    parser.add_argument("--with-code", action="store_true", help="Include key .py/.ts/.js source files")
    args = parser.parse_args()
    run_ingest(dry_run=args.dry_run, with_code=args.with_code)


if __name__ == "__main__":
    main()
