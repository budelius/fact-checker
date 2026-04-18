from pathlib import Path
from uuid import UUID, uuid4

from pypdf import PdfWriter

from app.ground_truth.acquisition import acquire_paper_pdf
from app.ground_truth.chunking import chunk_parsed_paper
from app.ground_truth.parsing import ParsedPaper, ParsedPaperPage, parse_pdf_to_pages
from app.schemas.ground_truth import (
    ExternalPaperId,
    PaperCandidate,
    PaperProcessingStatus,
)
from app.settings import Settings


def make_settings(monkeypatch, *, download_enabled: bool = True, max_pdf_mb: int = 40) -> Settings:
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", "../vault")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("PAPER_DOWNLOAD_ENABLED", "true" if download_enabled else "false")
    monkeypatch.setenv("PAPER_MAX_PDF_MB", str(max_pdf_mb))
    return Settings()


def make_candidate(**overrides: object) -> PaperCandidate:
    values = {
        "title": "Attention Is All You Need",
        "external_ids": [ExternalPaperId(provider="arxiv", value="1706.03762")],
        "source_url": "https://arxiv.org/abs/1706.03762",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
    }
    values.update(overrides)
    return PaperCandidate(**values)


class FakeResponse:
    def __init__(
        self,
        content: bytes,
        *,
        headers: dict[str, str] | None = None,
        status_code: int = 200,
        url: str = "https://arxiv.org/pdf/1706.03762.pdf",
    ) -> None:
        self.content = content
        self.headers = headers or {}
        self.status_code = status_code
        self.url = url


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.requests: list[dict[str, object]] = []

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        self.requests.append({"url": url, **kwargs})
        return self.response


def test_acquire_paper_metadata_only_when_download_disabled(monkeypatch, tmp_path):
    candidate = make_candidate()
    settings = make_settings(monkeypatch, download_enabled=False)

    acquisition = acquire_paper_pdf(candidate, tmp_path / "vault", settings, client=None)

    assert acquisition.status == PaperProcessingStatus.metadata_only
    assert acquisition.reason == "paper_download_disabled"
    assert acquisition.raw_pdf_path is None


def test_acquire_paper_metadata_only_without_pdf_url(monkeypatch, tmp_path):
    candidate = make_candidate(pdf_url=None)
    settings = make_settings(monkeypatch)

    acquisition = acquire_paper_pdf(candidate, tmp_path / "vault", settings, client=None)

    assert acquisition.status == PaperProcessingStatus.metadata_only
    assert acquisition.reason == "no_public_pdf_url"
    assert acquisition.raw_pdf_path is None


def test_acquire_paper_rejects_oversized_pdf(monkeypatch, tmp_path):
    candidate = make_candidate()
    settings = make_settings(monkeypatch, max_pdf_mb=1)
    client = FakeClient(
        FakeResponse(
            b"%PDF",
            headers={"content-type": "application/pdf", "content-length": str(1024 * 1024 + 1)},
        )
    )

    acquisition = acquire_paper_pdf(candidate, tmp_path / "vault", settings, client=client)

    assert acquisition.status == PaperProcessingStatus.metadata_only
    assert acquisition.reason == "pdf_too_large"
    assert acquisition.raw_pdf_path is None
    assert not (tmp_path / "vault" / "raw" / "papers").exists()


def test_acquire_paper_writes_public_pdf_to_raw_vault(monkeypatch, tmp_path):
    candidate = make_candidate()
    settings = make_settings(monkeypatch)
    pdf_bytes = Path("tests/fixtures/ground_truth/sample-paper.pdf").read_bytes()
    client = FakeClient(FakeResponse(pdf_bytes, headers={"content-type": "application/pdf"}))

    acquisition = acquire_paper_pdf(candidate, tmp_path / "vault", settings, client=client)

    assert acquisition.status == PaperProcessingStatus.downloaded
    assert acquisition.reason == "downloaded"
    assert acquisition.raw_pdf_path == (
        "vault/raw/papers/attention-is-all-you-need-arxiv-1706-03762.pdf"
    )
    assert acquisition.bytes_downloaded == len(pdf_bytes)
    assert (
        tmp_path / "vault" / "raw" / "papers" / "attention-is-all-you-need-arxiv-1706-03762.pdf"
    ).read_bytes() == pdf_bytes
    assert client.requests[0]["headers"] == {"Accept": "application/pdf"}


def test_parse_pdf_to_pages_extracts_text():
    paper_uuid = uuid4()

    parsed = parse_pdf_to_pages(
        paper_uuid,
        Path("tests/fixtures/ground_truth/sample-paper.pdf"),
    )

    assert parsed.status == PaperProcessingStatus.parsed
    assert parsed.reason is None
    assert parsed.pages[0].page_number == 1
    assert "Deterministic evidence text" in parsed.pages[0].text


def test_parse_pdf_to_pages_returns_metadata_only_for_empty_text(tmp_path):
    paper_uuid = uuid4()
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with pdf_path.open("wb") as pdf_file:
        writer.write(pdf_file)

    parsed = parse_pdf_to_pages(paper_uuid, pdf_path)

    assert parsed.status == PaperProcessingStatus.metadata_only
    assert parsed.reason == "text_unavailable"
    assert parsed.pages == []


def test_parse_pdf_to_pages_reports_parse_failure(tmp_path):
    pdf_path = tmp_path / "not-a-pdf.pdf"
    pdf_path.write_text("not a pdf", encoding="utf-8")

    parsed = parse_pdf_to_pages(uuid4(), pdf_path)

    assert parsed.status == PaperProcessingStatus.failed
    assert parsed.reason is not None
    assert parsed.reason.startswith("pdf_parse_failed:")
    assert parsed.pages == []


def test_chunk_parsed_paper_preserves_trace_fields():
    paper_uuid = UUID("00000000-0000-4000-8000-000000000001")
    source_uuid = UUID("00000000-0000-4000-8000-000000000002")
    parsed = ParsedPaper(
        paper_uuid=paper_uuid,
        pages=[ParsedPaperPage(page_number=7, text="Evidence text from a specific page.")],
        status=PaperProcessingStatus.parsed,
    )

    chunks = chunk_parsed_paper(
        paper_uuid,
        source_uuid,
        parsed,
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
        source_url="https://arxiv.org/abs/1706.03762",
    )

    assert len(chunks) == 1
    assert chunks[0].paper_uuid == paper_uuid
    assert chunks[0].source_uuid == source_uuid
    assert chunks[0].chunk_id == "paper-0007-0001"
    assert chunks[0].page_start == 7
    assert chunks[0].page_end == 7
    assert chunks[0].vault_path == "vault/wiki/papers/attention-is-all-you-need.md"
    assert chunks[0].source_url == "https://arxiv.org/abs/1706.03762"
    assert chunks[0].text == "Evidence text from a specific page."


def test_chunk_parsed_paper_uses_deterministic_chunk_ids():
    paper_uuid = uuid4()
    source_uuid = uuid4()
    parsed = ParsedPaper(
        paper_uuid=paper_uuid,
        pages=[
            ParsedPaperPage(page_number=1, text="A" * 12),
            ParsedPaperPage(page_number=3, text="B" * 12),
        ],
        status=PaperProcessingStatus.parsed,
    )

    chunks = chunk_parsed_paper(
        paper_uuid,
        source_uuid,
        parsed,
        vault_path="vault/wiki/papers/example.md",
        source_url="https://example.org/paper.pdf",
        max_chars=10,
        overlap_chars=2,
    )

    assert [chunk.chunk_id for chunk in chunks] == [
        "paper-0001-0001",
        "paper-0001-0002",
        "paper-0003-0003",
        "paper-0003-0004",
    ]
    assert [chunk.text for chunk in chunks] == ["A" * 10, "A" * 4, "B" * 10, "B" * 4]


def test_chunk_parsed_paper_skips_metadata_only():
    parsed = ParsedPaper(
        paper_uuid=uuid4(),
        pages=[],
        status=PaperProcessingStatus.metadata_only,
        reason="text_unavailable",
    )

    chunks = chunk_parsed_paper(
        uuid4(),
        uuid4(),
        parsed,
        vault_path="vault/wiki/papers/example.md",
        source_url="https://example.org/paper.pdf",
    )

    assert chunks == []
