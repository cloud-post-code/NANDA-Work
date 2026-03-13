"""
Query the NANDA Work knowledge base: embed question, retrieve top-k chunks, prompt LLM, print answer.
Run from NANDA Work root: python knowledge-base/query.py "Your question?" [--repo REPO] [--top-k N]
"""
import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    _kb_dir = Path(__file__).resolve().parent
    load_dotenv(_kb_dir / ".env")
    load_dotenv(_kb_dir.parent / ".env")
    load_dotenv()
except ImportError:
    pass

from config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
    LLM_MODEL,
)


def run_query(
    question: str,
    top_k: int = TOP_K,
    repo_filter: str | None = None,
    content_type_filter: str | None = None,
) -> str:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain_chroma import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    if not os.getenv("OPENAI_API_KEY"):
        return "Error: Set OPENAI_API_KEY in .env or environment."

    persist_dir = Path(CHROMA_PERSIST_DIR)
    if not (persist_dir / "chroma.sqlite3").exists() and not list(persist_dir.glob("*.sqlite3")):
        return "Error: No vector DB found. Run: python knowledge-base/ingest.py"

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
    )

    filter_dict = None
    if repo_filter or content_type_filter:
        filter_dict = {}
        if repo_filter:
            filter_dict["repo"] = repo_filter
        if content_type_filter:
            filter_dict["content_type"] = content_type_filter

    docs = vectorstore.similarity_search(question, k=top_k, filter=filter_dict)

    if not docs:
        return "No relevant chunks found. Try a different question or run ingest with --with-code."

    context_blocks = []
    for i, doc in enumerate(docs, 1):
        repo = doc.metadata.get("repo", "?")
        path = doc.metadata.get("file_path", "?")
        context_blocks.append(f"[{i}] Source: {repo}/{path}\n{doc.page_content}")

    context = "\n\n---\n\n".join(context_blocks)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You answer questions about the NANDA Work codebase using only the provided context.
If the context does not contain enough information, say so and do not invent details.
When possible, cite the source (repo and file path) in your answer."""),
        ("human", "Context:\n\n{context}\n\nQuestion: {question}\n\nAnswer:"),
    ])

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Query NANDA Work knowledge base")
    parser.add_argument("question", nargs="?", default="", help="Question to ask")
    parser.add_argument("--repo", type=str, default=None, help="Filter by repo")
    parser.add_argument("--content-type", type=str, default=None, choices=["doc", "schema", "code"])
    parser.add_argument("--top-k", type=int, default=TOP_K, help="Chunks to retrieve")
    args = parser.parse_args()

    question = args.question.strip()
    if not question:
        parser.print_help()
        sys.exit(0)

    answer = run_query(question=question, top_k=args.top_k, repo_filter=args.repo, content_type_filter=args.content_type)
    print(answer)


if __name__ == "__main__":
    main()
