from pathlib import Path
from uuid import UUID

from pydantic import BaseModel
from pypdf import PdfReader

from app.schemas.ground_truth import PaperProcessingStatus


class ParsedPaperPage(BaseModel):
    page_number: int
    text: str


class ParsedPaper(BaseModel):
    paper_uuid: UUID
    pages: list[ParsedPaperPage]
    status: PaperProcessingStatus
    reason: str | None = None


def _content_stream_size(page: object) -> int:
    contents = page.get_contents()
    if contents is None:
        return 0
    if isinstance(contents, list):
        return sum(len(content.get_data()) for content in contents)
    return len(contents.get_data())


def parse_pdf_to_pages(
    paper_uuid: UUID,
    pdf_path: Path,
    max_content_stream_bytes: int = 25_000_000,
) -> ParsedPaper:
    try:
        reader = PdfReader(pdf_path)
        pages: list[ParsedPaperPage] = []

        for index, page in enumerate(reader.pages, start=1):
            if _content_stream_size(page) > max_content_stream_bytes:
                raise ValueError("pdf_content_stream_too_large")

            text = (page.extract_text() or "").strip()
            if text:
                pages.append(ParsedPaperPage(page_number=index, text=text))

    except Exception as exc:
        return ParsedPaper(
            paper_uuid=paper_uuid,
            pages=[],
            status=PaperProcessingStatus.failed,
            reason=f"pdf_parse_failed:{type(exc).__name__}",
        )

    if not pages:
        return ParsedPaper(
            paper_uuid=paper_uuid,
            pages=[],
            status=PaperProcessingStatus.metadata_only,
            reason="text_unavailable",
        )

    return ParsedPaper(
        paper_uuid=paper_uuid,
        pages=pages,
        status=PaperProcessingStatus.parsed,
    )
