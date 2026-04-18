from uuid import UUID

from app.ground_truth.parsing import ParsedPaper
from app.schemas.ground_truth import PaperChunk, PaperProcessingStatus


def _text_windows(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    if max_chars <= 0:
        raise ValueError("max_chars_must_be_positive")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars_must_be_less_than_max_chars")

    stripped = text.strip()
    if not stripped:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(stripped):
        end = min(start + max_chars, len(stripped))
        chunks.append(stripped[start:end].strip())
        if end == len(stripped):
            break
        start = end - overlap_chars

    return [chunk for chunk in chunks if chunk]


def chunk_parsed_paper(
    paper_uuid: UUID,
    source_uuid: UUID,
    parsed: ParsedPaper,
    vault_path: str,
    source_url: str,
    max_chars: int = 3200,
    overlap_chars: int = 300,
) -> list[PaperChunk]:
    if parsed.status != PaperProcessingStatus.parsed:
        return []

    chunks: list[PaperChunk] = []
    chunk_index = 1
    for page in parsed.pages:
        for text in _text_windows(page.text, max_chars=max_chars, overlap_chars=overlap_chars):
            page_start = page.page_number
            chunks.append(
                PaperChunk(
                    paper_uuid=paper_uuid,
                    source_uuid=source_uuid,
                    chunk_id=f"paper-{page_start:04d}-{chunk_index:04d}",
                    text=text,
                    page_start=page_start,
                    page_end=page.page_number,
                    vault_path=vault_path,
                    source_url=source_url,
                )
            )
            chunk_index += 1

    return chunks
