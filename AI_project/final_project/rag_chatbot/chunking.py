import re
from dataclasses import dataclass

from . import config


@dataclass
class Chunk:
    chunk_id: str
    document_name: str
    source_path: str
    text: str
    chunk_index: int


def _split_into_sentences(text: str) -> list[str]:
    
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in sentences if s]


def chunk_text(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[str]:
    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            
            overlap_text = current[-overlap:] if overlap and current else ""
            current = f"{overlap_text} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks


def chunk_csv_rows(text: str, rows_per_chunk: int = config.ROWS_PER_CHUNK) -> list[str]:
    
    rows = [line for line in text.splitlines() if line.strip()]
    if not rows:
        return []
    return [
        "\n".join(rows[i:i + rows_per_chunk])
        for i in range(0, len(rows), rows_per_chunk)
    ]


def chunk_document(document) -> list[Chunk]:
    
    if getattr(document, "is_tabular", False):
        pieces = chunk_csv_rows(document.text)
    else:
        pieces = chunk_text(document.text)
    return [
        Chunk(
            chunk_id=f"{document.filename}::{i}",
            document_name=document.filename,
            source_path=document.source_path,
            text=piece,
            chunk_index=i,
        )
        for i, piece in enumerate(pieces)
    ]


def chunk_documents(documents: list) -> list[Chunk]:
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    return all_chunks