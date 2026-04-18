import ipaddress
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx

from app.contracts.vault import expected_raw_artifact_path
from app.schemas.ground_truth import (
    ExternalPaperId,
    PaperAcquisition,
    PaperCandidate,
    PaperProcessingStatus,
)
from app.settings import Settings


def is_public_pdf_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if parsed.username or parsed.password:
        return False

    hostname = parsed.hostname or ""
    if hostname.lower() == "localhost":
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and not address.is_global:
        return False

    path = unquote(parsed.path).lower()
    query = unquote(parsed.query).lower()
    if any(marker in path for marker in ("/login", "/signin", "/auth", "/account", "/paywall")):
        return False
    if any(marker in query for marker in ("token=", "signature=", "apikey=", "api_key=", "password=")):
        return False

    return path.endswith(".pdf") or "/pdf" in path or "format=pdf" in query


def safe_paper_slug(title: str, external_ids: list[ExternalPaperId]) -> str:
    base = title.strip().lower()
    if not base and external_ids:
        base = f"{external_ids[0].provider}-{external_ids[0].value}"

    slug = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    if not slug:
        slug = "paper"

    suffix = ""
    for external_id in external_ids:
        provider = re.sub(r"[^a-z0-9]+", "-", external_id.provider.lower()).strip("-")
        value = re.sub(r"[^a-z0-9]+", "-", external_id.value.lower()).strip("-")
        if provider and value:
            suffix = f"-{provider}-{value}"
            break

    max_base_length = max(24, 120 - len(suffix))
    return f"{slug[:max_base_length].strip('-')}{suffix}"


def _response_content_type(response: object) -> str:
    headers = getattr(response, "headers", {}) or {}
    return str(headers.get("content-type", headers.get("Content-Type", ""))).lower()


def _content_length(response: object) -> int | None:
    headers = getattr(response, "headers", {}) or {}
    raw_length = headers.get("content-length", headers.get("Content-Length"))
    if raw_length is None:
        return None
    try:
        return int(raw_length)
    except (TypeError, ValueError):
        return None


def _client_get(client: object, url: str, settings: Settings) -> object:
    headers = {"Accept": "application/pdf"}
    try:
        return client.get(
            url,
            headers=headers,
            timeout=settings.paper_request_timeout_seconds,
            follow_redirects=True,
        )
    except TypeError:
        return client.get(url, headers=headers)


def acquire_paper_pdf(
    candidate: PaperCandidate,
    vault_root: Path,
    settings: Settings,
    client: object | None = None,
) -> PaperAcquisition:
    source_url = candidate.source_url or candidate.landing_page_url or candidate.pdf_url

    if not settings.paper_download_enabled:
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason="paper_download_disabled",
        )

    if not candidate.pdf_url or not is_public_pdf_url(candidate.pdf_url):
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason="no_public_pdf_url",
        )

    owns_client = client is None
    active_client = client or httpx.Client()
    try:
        response = _client_get(active_client, candidate.pdf_url, settings)
    except Exception as exc:
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason=f"pdf_download_failed:{type(exc).__name__}",
        )
    finally:
        if owns_client:
            active_client.close()

    final_url = str(getattr(response, "url", candidate.pdf_url))
    if not is_public_pdf_url(final_url):
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason="no_public_pdf_url",
        )

    status_code = getattr(response, "status_code", 200)
    if status_code >= 400:
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason=f"pdf_download_failed:{status_code}",
        )

    max_bytes = settings.paper_max_pdf_mb * 1024 * 1024
    content_length = _content_length(response)
    if content_length is not None and content_length > max_bytes:
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason="pdf_too_large",
        )

    content = getattr(response, "content", b"")
    if len(content) > max_bytes:
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason="pdf_too_large",
        )

    content_type = _response_content_type(response)
    if "pdf" not in content_type and not content.startswith(b"%PDF"):
        return PaperAcquisition(
            paper_uuid=candidate.uuid,
            source_url=source_url,
            pdf_url=candidate.pdf_url,
            status=PaperProcessingStatus.metadata_only,
            reason="not_pdf_response",
        )

    slug = safe_paper_slug(candidate.title, candidate.external_ids)
    raw_pdf_path = expected_raw_artifact_path("papers", slug, "pdf")
    absolute_pdf_path = vault_root / "raw" / "papers" / f"{slug}.pdf"
    absolute_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_pdf_path.write_bytes(content)

    return PaperAcquisition(
        paper_uuid=candidate.uuid,
        source_url=source_url,
        pdf_url=candidate.pdf_url,
        raw_pdf_path=raw_pdf_path,
        status=PaperProcessingStatus.downloaded,
        reason="downloaded",
        bytes_downloaded=len(content),
    )
