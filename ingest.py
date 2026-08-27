from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader
from tqdm import tqdm

from chunking import chunk_text
from config import load_settings
from doc_registry import register_document
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore


def extract_pdf_pages(path: Path) -> list[str]:
    """
    Extract PDF text page-by-page.

    The returned list is 0-indexed internally:
    index 0 = PDF page 1
    index 1 = PDF page 2
    etc.
    """

    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return pages


def extract_pdf_text(path: Path) -> str:
    """
    Extract the complete PDF text.
    """

    pages = extract_pdf_pages(path)

    return "\n\n".join(pages)


def extract_text(path: Path) -> str:

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(path)

    if extension in {".txt", ".md"}:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    raise ValueError(
        "Only PDF, MD, and TXT files are supported."
    )


def iter_document_paths(target: Path) -> list[Path]:

    allowed = {
        ".pdf",
        ".md",
        ".txt",
    }

    if target.is_file():
        return (
            [target]
            if target.suffix.lower() in allowed
            else []
        )

    return sorted(
        path
        for path in target.rglob("*")
        if path.is_file()
        and path.suffix.lower() in allowed
    )


def ingest_file(
    path: Path,
    store: QdrantStore,
    embedder: GeminiEmbedder,
    settings,
    user_id: int,
    original_filename: str | None = None,
) -> dict:

    extension = path.suffix.lower()

    # ---------------------------------------------------------
    # EXTRACT TEXT
    # ---------------------------------------------------------

    if extension == ".pdf":

        pdf_pages = extract_pdf_pages(path)

        if not pdf_pages:
            raise ValueError(
                "PDF contains no pages."
            )

        if not any(
            page.strip()
            for page in pdf_pages
        ):
            raise ValueError(
                "No extractable text found in document."
            )

        full_text = "\n\n".join(
            pdf_pages
        )

    else:

        full_text = extract_text(path)

        if not full_text.strip():
            raise ValueError(
                "No extractable text found in document."
            )

        pdf_pages = None

    # ---------------------------------------------------------
    # CHUNK DOCUMENT
    # ---------------------------------------------------------

    chunk_texts: list[str] = []
    page_numbers: list[int | None] = []

    if extension == ".pdf":

        # IMPORTANT:
        # Chunk each PDF page separately so every chunk
        # knows which page it came from.

        for page_index, page_text in enumerate(
            pdf_pages
        ):

            if not page_text.strip():
                continue

            page_chunks = chunk_text(
                page_text,
                settings.chunk_size_tokens,
                settings.chunk_overlap_tokens,
            )

            for chunk in page_chunks:

                if not chunk.text.strip():
                    continue

                chunk_texts.append(
                    chunk.text
                )

                # PDF pages are 1-indexed for users.
                page_numbers.append(
                    page_index + 1
                )

    else:

        chunks = chunk_text(
            full_text,
            settings.chunk_size_tokens,
            settings.chunk_overlap_tokens,
        )

        for chunk in chunks:

            if not chunk.text.strip():
                continue

            chunk_texts.append(
                chunk.text
            )

            # TXT/MD files do not currently have
            # reliable page numbers.
            page_numbers.append(None)

    if not chunk_texts:
        raise ValueError(
            "Document produced 0 chunks."
        )

    # ---------------------------------------------------------
    # CREATE EMBEDDINGS
    # ---------------------------------------------------------

    vectors = embedder.embed_documents(
        chunk_texts
    )

    if len(vectors) != len(chunk_texts):
        raise ValueError(
            "Number of embeddings does not match "
            "number of chunks."
        )

    # ---------------------------------------------------------
    # FILE NAME
    # ---------------------------------------------------------

    filename = (
        original_filename
        if original_filename
        else path.name
    )

    title = Path(filename).stem

    title = (
        title
        .replace("_", " ")
        .replace("-", " ")
    )

    # ---------------------------------------------------------
    # REGISTER DOCUMENT IN DATABASE
    # ---------------------------------------------------------

    doc_id = register_document(
        source_path=filename,
        title=title,
        full_text=full_text,
        num_chunks=len(chunk_texts),
        user_id=user_id,
    )

    # ---------------------------------------------------------
    # SAVE CHUNKS + PAGE NUMBERS IN QDRANT
    # ---------------------------------------------------------

    store.upsert_chunks(
        doc_id=doc_id,
        title=title,
        source=filename,
        chunk_texts=chunk_texts,
        embeddings=vectors,
        user_id=user_id,
        page_numbers=page_numbers,
    )

    print(
        f"  + {filename}: "
        f"{len(chunk_texts)} chunks -> "
        f"doc_id={doc_id}"
    )

    return {
        "doc_id": doc_id,
        "title": title,
        "filename": filename,
        "num_chunks": len(chunk_texts),
    }


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Ingest PDF/MD/TXT documents into the Qdrant-backed "
            "personal knowledge base."
        )
    )

    parser.add_argument(
        "path",
        help="Path to a document or a folder of documents.",
    )

    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        help=(
            "Owner id to tag ingested chunks with. Defaults to "
            "MCP_DEFAULT_USER_ID from .env (used by the standalone "
            "MCP server / Claude Desktop demo)."
        ),
    )

    args = parser.parse_args()

    target = (
        Path(args.path)
        .expanduser()
        .resolve()
    )

    if not target.exists():

        print(
            f"Path does not exist: {target}"
        )

        sys.exit(1)

    settings = load_settings()

    user_id = (
        args.user_id
        if args.user_id is not None
        else settings.mcp_default_user_id
    )

    store = QdrantStore(settings)

    store.ensure_collection()

    embedder = GeminiEmbedder(settings)

    document_paths = iter_document_paths(
        target
    )

    if not document_paths:

        print(
            f"No PDF, MD, or TXT files found at {target}"
        )

        sys.exit(1)

    print(
        f"Ingesting {len(document_paths)} "
        f"document(s) into collection "
        f"'{settings.qdrant_collection}' as user_id={user_id}..."
    )

    results = []

    for path in tqdm(
        document_paths,
        desc="Documents",
        unit="doc",
    ):

        try:
            result = ingest_file(
                path=path,
                store=store,
                embedder=embedder,
                settings=settings,
                user_id=user_id,
            )
            results.append(result)
        except Exception as e:  # noqa: BLE001
            print(f"  ! Failed to ingest {path.name}: {e}")

    print(
        f"Done. Ingested {len(results)}/{len(document_paths)} document(s)."
    )


if __name__ == "__main__":
    main()